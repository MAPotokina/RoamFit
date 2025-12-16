"""Workout Management functions for ROAMFIT."""
from typing import Any, Dict, List, Optional

from database import (
    delete_workout,
    get_workout_by_id,
    get_workout_history,
    update_workout,
    update_workout_completion,
)


def list_workouts(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent workouts."""
    return get_workout_history(limit=limit)


def get_workout(workout_id: int) -> Optional[Dict[str, Any]]:
    """Get workout by ID."""
    return get_workout_by_id(workout_id)


def edit_workout(
    workout_id: int,
    equipment: Optional[List[str]] = None,
    workout_plan: Optional[Dict[str, Any]] = None,
    location: Optional[str] = None,
    completed: Optional[bool] = None,
) -> Dict[str, Any]:
    """Edit workout fields."""
    success = update_workout(
        workout_id=workout_id,
        equipment=equipment,
        workout_plan=workout_plan,
        location=location,
        completed=completed,
    )
    if success:
        updated = get_workout_by_id(workout_id)
        return {
            "success": True,
            "message": f"Workout #{workout_id} updated successfully",
            "workout": updated,
        }
    else:
        return {
            "success": False,
            "message": f"Failed to update workout #{workout_id}",
            "workout": None,
        }


def remove_workout(workout_id: int) -> Dict[str, Any]:
    """Delete workout by ID."""
    workout = get_workout_by_id(workout_id)
    if not workout:
        return {"success": False, "message": f"Workout #{workout_id} not found"}

    success = delete_workout(workout_id)
    if success:
        return {"success": True, "message": f"Workout #{workout_id} deleted successfully"}
    else:
        return {"success": False, "message": f"Failed to delete workout #{workout_id}"}


def mark_workout_complete(workout_id: int, completed: bool = True) -> Dict[str, Any]:
    """Mark workout as completed or incomplete."""
    success = update_workout_completion(workout_id, completed)
    if success:
        workout = get_workout_by_id(workout_id)
        status = "completed" if completed else "incomplete"
        return {
            "success": True,
            "message": f"Workout #{workout_id} marked as {status}",
            "workout": workout,
        }
    else:
        return {"success": False, "message": f"Failed to update workout #{workout_id}"}
