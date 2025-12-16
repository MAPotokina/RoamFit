"""Database operations for ROAMFIT."""
import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import get_config
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    config = get_config()
    conn = sqlite3.connect(config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables():
    """Create all database tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                equipment TEXT NOT NULL,
                workout_plan TEXT NOT NULL,
                location TEXT,
                completed INTEGER DEFAULT 0
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS equipment_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_path TEXT NOT NULL,
                detected_equipment TEXT NOT NULL,
                location TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0,
                time_ms INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL
            )
        """
        )


def save_workout(
    equipment: List[str],
    workout_plan: Dict,
    location: Optional[str] = None,
    completed: bool = False,
) -> int:
    """Save a workout to database. Returns workout ID."""
    try:
        logger.info(
            f"Saving workout: equipment={equipment}, location={location}, completed={completed}"
        )
        date = datetime.now().isoformat()
        equipment_json = json.dumps(equipment)
        workout_plan_json = json.dumps(workout_plan)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workouts (date, equipment, workout_plan, location, completed)
                VALUES (?, ?, ?, ?, ?)
            """,
                (date, equipment_json, workout_plan_json, location, 1 if completed else 0),
            )
            workout_id = int(cursor.lastrowid) if cursor.lastrowid else 0
            logger.info(f"Workout saved successfully with ID: {workout_id}")
            return workout_id
    except Exception as e:
        logger.error(f"Failed to save workout: {str(e)}", exc_info=True)
        raise DatabaseError(
            message=f"Failed to save workout: {str(e)}",
            operation="save_workout",
            details={"equipment": equipment, "location": location},
        )


def get_last_workout() -> Optional[Dict]:
    """Get the most recent workout. Returns None if no workouts exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM workouts
            ORDER BY date DESC
            LIMIT 1
        """
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "date": row["date"],
            "equipment": json.loads(row["equipment"]),
            "workout_plan": json.loads(row["workout_plan"]),
            "location": row["location"],
            "completed": bool(row["completed"]),
        }


def get_workout_history(limit: int = 5) -> List[Dict]:
    """Get recent workout history. Returns list of workouts."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM workouts
            ORDER BY date DESC
            LIMIT ?
        """,
            (limit,),
        )
        rows = cursor.fetchall()

        workouts = []
        for row in rows:
            workouts.append(
                {
                    "id": row["id"],
                    "date": row["date"],
                    "equipment": json.loads(row["equipment"]),
                    "workout_plan": json.loads(row["workout_plan"]),
                    "location": row["location"],
                    "completed": bool(row["completed"]),
                }
            )

        return workouts


def update_workout_completion(workout_id: int, completed: bool = True) -> bool:
    """Update workout completion status. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE workouts
            SET completed = ?
            WHERE id = ?
        """,
            (1 if completed else 0, workout_id),
        )
        return bool(cursor.rowcount > 0)


def get_workout_by_id(workout_id: int) -> Optional[Dict]:
    """Get workout by ID. Returns None if not found."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM workouts
            WHERE id = ?
        """,
            (workout_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "date": row["date"],
            "equipment": json.loads(row["equipment"]),
            "workout_plan": json.loads(row["workout_plan"]),
            "location": row["location"],
            "completed": bool(row["completed"]),
        }


def update_workout(
    workout_id: int,
    equipment: Optional[List[str]] = None,
    workout_plan: Optional[Dict] = None,
    location: Optional[str] = None,
    completed: Optional[bool] = None,
) -> bool:
    """Update workout fields. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get existing workout
        cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
        row = cursor.fetchone()
        if row is None:
            return False

        # Update only provided fields
        updates: List[str] = []
        values: List[Any] = []

        if equipment is not None:
            updates.append("equipment = ?")
            values.append(json.dumps(equipment))

        if workout_plan is not None:
            updates.append("workout_plan = ?")
            values.append(json.dumps(workout_plan))

        if location is not None:
            updates.append("location = ?")
            values.append(location)

        if completed is not None:
            updates.append("completed = ?")
            values.append(1 if completed else 0)

        if not updates:
            return False

        values.append(workout_id)

        query = f"UPDATE workouts SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        return bool(cursor.rowcount > 0)


def delete_workout(workout_id: int) -> bool:
    """Delete workout by ID. Returns True if successful."""
    try:
        logger.info(f"Deleting workout ID: {workout_id}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
            success = bool(cursor.rowcount > 0)
            if success:
                logger.info(f"Workout {workout_id} deleted successfully")
            else:
                logger.warning(f"Workout {workout_id} not found for deletion")
            return success
    except Exception as e:
        logger.error(f"Failed to delete workout {workout_id}: {str(e)}", exc_info=True)
        raise DatabaseError(
            message=f"Failed to delete workout: {str(e)}",
            operation="delete_workout",
            details={"workout_id": workout_id},
        )


def save_equipment_detection(
    image_path: str, detected_equipment: List[str], location: Optional[str] = None
) -> int:
    """Save equipment detection result. Returns detection ID."""
    timestamp = datetime.now().isoformat()
    equipment_json = json.dumps(detected_equipment)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO equipment_detections
            (timestamp, image_path, detected_equipment, location)
            VALUES (?, ?, ?, ?)
        """,
            (timestamp, image_path, equipment_json, location),
        )
        return int(cursor.lastrowid) if cursor.lastrowid else 0


def save_llm_log(
    agent_name: str,
    model: str,
    status: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    time_ms: int = 0,
    error_message: Optional[str] = None,
) -> int:
    """Save LLM call log to database. Returns log ID."""
    timestamp = datetime.now().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO llm_logs
            (agent_name, model, status, tokens_in, tokens_out, time_ms, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (agent_name, model, status, tokens_in, tokens_out, time_ms, error_message, timestamp),
        )
        return int(cursor.lastrowid) if cursor.lastrowid else 0


def get_llm_stats() -> Dict:
    """Get aggregated LLM usage statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Overall statistics
        cursor.execute("SELECT COUNT(*) as total FROM llm_logs")
        total_calls = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM llm_logs WHERE status = 'SUCCESS'")
        successful_calls = cursor.fetchone()["total"]

        cursor.execute("SELECT SUM(tokens_in + tokens_out) as total FROM llm_logs")
        total_tokens = cursor.fetchone()["total"] or 0

        # Breakdown by agent
        cursor.execute(
            """
            SELECT
                agent_name,
                COUNT(*) as call_count,
                SUM(tokens_in + tokens_out) as tokens_used,
                AVG(time_ms) as avg_time_ms,
                SUM(tokens_in) as tokens_in_sum,
                SUM(tokens_out) as tokens_out_sum
            FROM llm_logs
            GROUP BY agent_name
            ORDER BY call_count DESC
        """
        )
        agent_stats = []
        for row in cursor.fetchall():
            agent_stats.append(
                {
                    "agent_name": row["agent_name"],
                    "call_count": row["call_count"],
                    "tokens_used": row["tokens_used"] or 0,
                    "avg_time_ms": round(row["avg_time_ms"] or 0, 2),
                    "tokens_in": row["tokens_in_sum"] or 0,
                    "tokens_out": row["tokens_out_sum"] or 0,
                }
            )

        # Breakdown by model
        cursor.execute(
            """
            SELECT
                model,
                COUNT(*) as call_count,
                SUM(tokens_in + tokens_out) as tokens_used,
                SUM(tokens_in) as tokens_in_sum,
                SUM(tokens_out) as tokens_out_sum
            FROM llm_logs
            GROUP BY model
            ORDER BY call_count DESC
        """
        )
        model_stats = []
        for row in cursor.fetchall():
            model_stats.append(
                {
                    "model": row["model"],
                    "call_count": row["call_count"],
                    "tokens_used": row["tokens_used"] or 0,
                    "tokens_in": row["tokens_in_sum"] or 0,
                    "tokens_out": row["tokens_out_sum"] or 0,
                }
            )

        # Calculate estimated cost
        # GPT-4: $0.03/1K input, $0.06/1K output
        # GPT-4o: $0.0025/1K input, $0.01/1K output
        estimated_cost = 0.0
        for model_stat in model_stats:
            model = model_stat["model"]
            tokens_in = model_stat["tokens_in"]
            tokens_out = model_stat["tokens_out"]

            if "gpt-4o" in model.lower():
                cost = (tokens_in / 1000) * 0.0025 + (tokens_out / 1000) * 0.01
            elif "gpt-4" in model.lower():
                cost = (tokens_in / 1000) * 0.03 + (tokens_out / 1000) * 0.06
            else:
                # Default estimate
                cost = ((tokens_in + tokens_out) / 1000) * 0.008
            estimated_cost += cost

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "total_tokens": total_tokens,
            "estimated_cost": round(estimated_cost, 4),
            "by_agent": agent_stats,
            "by_model": model_stats,
        }
