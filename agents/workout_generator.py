"""Workout Generator Agent for ROAMFIT."""
import json
from typing import List, Dict, Any, Optional
from utils.llm import call_llm


def generate_workout(
    equipment: List[str],
    workout_history: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate workout plan based on equipment and history."""
    if not equipment:
        return {
            "exercises": [],
            "duration_minutes": 0,
            "focus": "none",
            "error": "No equipment provided"
        }
    
    # Format equipment list
    equipment_text = ", ".join(equipment)
    
    # Format workout history if provided
    history_text = ""
    if workout_history and workout_history.get("summary"):
        history_text = f"\nPrevious workout summary: {workout_history['summary']}\n"
        history_text += f"Last workout date: {workout_history.get('last_workout_date', 'Unknown')}\n"
        history_text += f"Total previous workouts: {workout_history.get('total_workouts', 0)}\n"
    
    # Create prompt requesting JSON response
    prompt = f"""Generate a personalized workout plan based on the available equipment and workout history.

Available Equipment: {equipment_text}
{history_text}

Create a workout plan that:
- Uses only the available equipment listed above
- Varies exercises from previous workouts (if history provided)
- Includes proper warm-up and cool-down suggestions
- Provides clear instructions for each exercise

Return your response as a JSON object with this exact format:
{{
  "exercises": [
    {{
      "name": "Exercise Name",
      "sets": 3,
      "reps": 10,
      "rest_seconds": 60,
      "instructions": "Brief instructions for proper form"
    }}
  ],
  "duration_minutes": 30,
  "focus": "upper_body" or "lower_body" or "full_body" or "cardio",
  "warmup": "Brief warm-up suggestions",
  "cooldown": "Brief cool-down suggestions"
}}

Include 4-6 exercises that can be done with the available equipment.
JSON response:"""
    
    try:
        # Call LLM
        response_text = call_llm(prompt, agent_name="workout_generator")
        
        # Parse JSON response
        response_text = response_text.strip()
        
        # Find JSON object in response
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = response_text[start_idx:end_idx]
        workout_plan = json.loads(json_str)
        
        # Validate structure
        if "exercises" not in workout_plan:
            workout_plan["exercises"] = []
        if "duration_minutes" not in workout_plan:
            workout_plan["duration_minutes"] = 0
        if "focus" not in workout_plan:
            workout_plan["focus"] = "full_body"
        
        return workout_plan
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return error
        return {
            "exercises": [],
            "duration_minutes": 0,
            "focus": "none",
            "error": f"Failed to parse JSON response: {str(e)}"
        }
    except Exception as e:
        raise Exception(f"Workout generation failed: {str(e)}")

