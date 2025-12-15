"""Database operations for ROAMFIT."""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager
from config import get_config


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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                equipment TEXT NOT NULL,
                workout_plan TEXT NOT NULL,
                location TEXT,
                completed INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_path TEXT NOT NULL,
                detected_equipment TEXT NOT NULL,
                location TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        """)


def save_workout(
    equipment: List[str],
    workout_plan: Dict,
    location: Optional[str] = None,
    completed: bool = False
) -> int:
    """Save a workout to database. Returns workout ID."""
    date = datetime.now().isoformat()
    equipment_json = json.dumps(equipment)
    workout_plan_json = json.dumps(workout_plan)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workouts (date, equipment, workout_plan, location, completed)
            VALUES (?, ?, ?, ?, ?)
        """, (date, equipment_json, workout_plan_json, location, 1 if completed else 0))
        return cursor.lastrowid


def get_last_workout() -> Optional[Dict]:
    """Get the most recent workout. Returns None if no workouts exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workouts
            ORDER BY date DESC
            LIMIT 1
        """)
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
        cursor.execute("""
            SELECT * FROM workouts
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        workouts = []
        for row in rows:
            workouts.append({
                "id": row["id"],
                "date": row["date"],
                "equipment": json.loads(row["equipment"]),
                "workout_plan": json.loads(row["workout_plan"]),
                "location": row["location"],
                "completed": bool(row["completed"]),
            })
        
        return workouts


def save_equipment_detection(
    image_path: str,
    detected_equipment: List[str],
    location: Optional[str] = None
) -> int:
    """Save equipment detection result. Returns detection ID."""
    timestamp = datetime.now().isoformat()
    equipment_json = json.dumps(detected_equipment)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipment_detections 
            (timestamp, image_path, detected_equipment, location)
            VALUES (?, ?, ?, ?)
        """, (timestamp, image_path, equipment_json, location))
        return cursor.lastrowid

