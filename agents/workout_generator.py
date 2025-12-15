"""Workout Generator Agent for ROAMFIT."""
import json
from typing import List, Dict, Any, Optional
from utils.llm import call_llm
from database import save_workout


def generate_workout(
    equipment: List[str],
    workout_history: Optional[Dict[str, Any]] = None,
    location: Optional[str] = None,
    save_to_db: bool = True
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
    prompt = f"""Generate a CrossFit-style workout plan in whiteboard format (CONCISE, no long descriptions).

Available Equipment: {equipment_text}
{history_text}

Create a CrossFit workout that:
- Uses only the available equipment listed above
- Uses CrossFit formats: EMOM, AMRAP, For Time, Rounds for Time, Tabata, or Chipper
- Varies exercises and formats from previous workouts (if history provided)
- Keep it CONCISE like a CrossFit whiteboard - just format, exercises, and reps

Return your response as a JSON object with this exact format:
{{
  "format": "EMOM" or "AMRAP" or "For Time" or "Rounds for Time" or "Tabata" or "Chipper",
  "duration_minutes": 20,
  "exercises": [
    {{
      "name": "Exercise Name",
      "reps": 10,
      "instructions": ""
    }}
  ],
  "workout_description": "Brief whiteboard-style description (one line, e.g., 'AMRAP 15: 10 Thrusters, 15 Burpees')",
  "focus": "upper_body" or "lower_body" or "full_body" or "cardio",
  "warmup": "Brief warm-up (one line)",
  "cooldown": "Brief cool-down (one line)"
}}

IMPORTANT - WHITEBOARD STYLE:
- Keep exercise names SHORT and clear (e.g., "Dumbbell Thrusters", "Burpees", "Pull-ups")
- Leave "instructions" field EMPTY or very brief (max 5 words)
- Workout description should be whiteboard-style (e.g., "EMOM 12: Min 1-3 Thrusters, Min 4-6 Burpees")
- For EMOM: format like "EMOM 12: Min 1-3 [exercise] [reps], Min 4-6 [exercise] [reps]"
- For AMRAP: format like "AMRAP 15: [exercise] [reps], [exercise] [reps]"
- For For Time: format like "For Time: [exercise] [reps], [exercise] [reps]"
- Include 3-5 exercises that can be done with the available equipment
- Make it challenging but achievable
- NO long descriptions - keep it like a whiteboard!

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
        if "format" not in workout_plan:
            workout_plan["format"] = "AMRAP"  # Default CrossFit format
        if "exercises" not in workout_plan:
            workout_plan["exercises"] = []
        if "duration_minutes" not in workout_plan:
            workout_plan["duration_minutes"] = 20  # Typical CrossFit workout duration
        if "focus" not in workout_plan:
            workout_plan["focus"] = "full_body"
        if "workout_description" not in workout_plan:
            # Generate description if missing
            format_name = workout_plan.get("format", "AMRAP")
            workout_plan["workout_description"] = f"Perform this workout as {format_name}"
        
        # Save workout to database if requested
        if save_to_db and not workout_plan.get("error"):
            try:
                workout_id = save_workout(
                    equipment=equipment,
                    workout_plan=workout_plan,
                    location=location,
                    completed=False
                )
                workout_plan["workout_id"] = workout_id
            except Exception as e:
                # Don't fail if saving fails, just log it
                workout_plan["save_error"] = str(e)
        
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

