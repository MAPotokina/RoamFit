"""Orchestrator Agent for ROAMFIT - coordinates all agents."""
from typing import Dict, Any, Optional, List
from agents.equipment_detection import detect_equipment
from agents.workout_summary import summarize_workout_history
from agents.workout_generator import generate_workout


def generate_workout_flow(
    image_path: Optional[str] = None,
    location: Optional[str] = None,
    equipment: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Main workflow: equipment detection → history → workout generation.
    
    Args:
        image_path: Path to equipment photo (optional)
        location: Location string (optional)
        equipment: Direct equipment list (optional, if image_path not provided)
    
    Returns:
        Dict with workout plan and metadata
    """
    detected_equipment = []
    detection_id = None
    
    # Step 1: Detect equipment from image if provided
    if image_path:
        try:
            detection_result = detect_equipment(image_path, location=location)
            detected_equipment = detection_result.get("equipment", [])
            detection_id = detection_result.get("detection_id")
        except Exception as e:
            return {
                "error": f"Equipment detection failed: {str(e)}",
                "workout_plan": None
            }
    elif equipment:
        # Use provided equipment list
        detected_equipment = equipment
    else:
        return {
            "error": "Either image_path or equipment list must be provided",
            "workout_plan": None
        }
    
    if not detected_equipment:
        return {
            "error": "No equipment detected or provided",
            "workout_plan": None,
            "equipment": []
        }
    
    # Step 2: Get workout history summary
    try:
        workout_history = summarize_workout_history(limit=5)
    except Exception as e:
        # Continue without history if summary fails
        workout_history = {
            "summary": "Unable to retrieve workout history",
            "last_workout_date": None,
            "total_workouts": 0
        }
    
    # Step 3: Generate workout plan
    try:
        workout_plan = generate_workout(
            equipment=detected_equipment,
            workout_history=workout_history
        )
    except Exception as e:
        return {
            "error": f"Workout generation failed: {str(e)}",
            "workout_plan": None,
            "equipment": detected_equipment,
            "workout_history": workout_history
        }
    
    # Return unified response
    return {
        "workout_plan": workout_plan,
        "equipment": detected_equipment,
        "workout_history": workout_history,
        "detection_id": detection_id,
        "error": None
    }

