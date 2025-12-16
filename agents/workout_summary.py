"""Workout Summary Agent for ROAMFIT."""
from typing import Any, Dict, Optional

from database import get_last_workout as db_get_last_workout
from database import get_workout_history
from models.schemas import WorkoutHistory
from utils.llm import call_llm


def get_last_workout() -> Optional[Dict[str, Any]]:
    """Get the most recent workout. Returns None if no workouts exist."""
    return db_get_last_workout()


def summarize_workout_history(limit: int = 5) -> Dict[str, Any]:
    """
    Summarize recent workout history using LLM.

    Returns dict compatible with WorkoutHistory model.
    """
    workouts = get_workout_history(limit)

    if not workouts:
        history = WorkoutHistory(
            summary="No workout history available.", last_workout_date=None, total_workouts=0
        )
        return history.to_dict()

    # Format workouts for LLM prompt
    workout_text = ""
    for workout in workouts:
        workout_text += f"\nDate: {workout['date']}\n"
        workout_text += f"Equipment: {', '.join(workout['equipment'])}\n"
        workout_text += f"Location: {workout['location'] or 'Not specified'}\n"
        workout_text += f"Completed: {'Yes' if workout['completed'] else 'No'}\n"
        workout_text += f"Workout Plan: {workout['workout_plan']}\n"
        workout_text += "---\n"

    prompt = f"""Summarize the following workout history in 2-3 sentences.
Focus on patterns, equipment usage, and overall progress.

Workout History:
{workout_text}

Provide a concise summary:"""

    summary = call_llm(prompt, agent_name="workout_summary")

    history = WorkoutHistory(
        summary=summary,
        last_workout_date=workouts[0]["date"] if workouts else None,
        total_workouts=len(workouts),
    )
    return history.to_dict()
