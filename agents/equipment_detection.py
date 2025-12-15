"""Equipment Detection Agent for ROAMFIT."""
import json
from pathlib import Path
from typing import List, Dict, Any
from utils.llm import call_vision
from database import save_equipment_detection
from models.schemas import EquipmentDetection


def detect_equipment(
    image_path: str,
    location: str = None
) -> Dict[str, Any]:
    """Detect equipment from image. Returns equipment list and detection ID."""
    # Validate image file exists
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Create prompt requesting JSON response
    prompt = """Analyze this image and identify all fitness equipment visible.
Return your response as a JSON object with this exact format:
{"equipment": ["equipment_name1", "equipment_name2", ...]}

List only actual fitness equipment (dumbbells, benches, resistance bands, etc.).
Use simple, lowercase names with underscores (e.g., "dumbbells", "yoga_mat", "resistance_bands").
If no equipment is visible, return: {"equipment": []}

JSON response:"""
    
    try:
        # Call vision API
        response_text = call_vision(
            image_path=image_path,
            prompt=prompt,
            agent_name="equipment_detection"
        )
        
        # Parse JSON response
        # Try to extract JSON from response (might have extra text)
        response_text = response_text.strip()
        
        # Find JSON object in response
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = response_text[start_idx:end_idx]
        parsed = json.loads(json_str)
        
        equipment_list = parsed.get("equipment", [])
        
        if not isinstance(equipment_list, list):
            equipment_list = []
        
        # Save to database
        detection_id = save_equipment_detection(
            image_path=image_path,
            detected_equipment=equipment_list,
            location=location
        )
        
        detection = EquipmentDetection(
            equipment=equipment_list,
            detection_id=detection_id,
            image_path=image_path,
            location=location
        )
        return detection.to_dict()
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return empty list
        equipment_list = []
        detection_id = save_equipment_detection(
            image_path=image_path,
            detected_equipment=equipment_list,
            location=location
        )
        detection = EquipmentDetection(
            equipment=equipment_list,
            detection_id=detection_id,
            image_path=image_path,
            location=location,
            error=f"Failed to parse JSON response: {str(e)}"
        )
        return detection.to_dict()
    except Exception as e:
        # Handle other errors
        raise Exception(f"Equipment detection failed: {str(e)}")

