"""Input validation utilities for ROAMFIT."""
import re
from typing import List, Optional, Tuple, Any
from pathlib import Path
from utils.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Allowed equipment names (case-insensitive)
ALLOWED_EQUIPMENT = {
    "dumbbells", "barbell", "kettlebell", "kettlebells",
    "bench", "pull-up bar", "pull up bar", "pullup bar",
    "resistance bands", "resistance band", "bands",
    "yoga mat", "mat", "medicine ball", "medicine balls",
    "jump rope", "rope", "box", "plyo box", "plyometric box",
    "rower", "rowing machine", "bike", "bicycle", "stationary bike",
    "treadmill", "elliptical", "squat rack", "rack",
    "cable machine", "cables", "trx", "suspension trainer",
    "ab wheel", "foam roller", "roller",
    "none", "bodyweight", "body weight", "no equipment"
}

# Maximum image size (10MB default)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed image types
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


def validate_image_file(
    file_content: bytes,
    filename: Optional[str] = None,
    max_size: int = MAX_IMAGE_SIZE
) -> Tuple[bool, Optional[str]]:
    """
    Validate image file.
    Returns (is_valid, error_message)
    """
    # Check file size
    if len(file_content) > max_size:
        return False, f"Image file too large. Maximum size is {max_size / (1024*1024):.0f}MB"
    
    if len(file_content) == 0:
        return False, "Image file is empty"
    
    # Check file extension if filename provided
    if filename:
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    # Check magic bytes (basic image validation)
    if file_content[:2] == b'\xff\xd8':  # JPEG
        return True, None
    elif file_content[:8] == b'\x89PNG\r\n\x1a\n':  # PNG
        return True, None
    elif filename and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        # If extension is valid, accept it (magic bytes check is best-effort)
        return True, None
    
    return False, "Invalid image format. Only JPEG and PNG are supported"


def validate_equipment_list(equipment: List[str]) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate equipment list.
    Returns (is_valid, error_message, normalized_equipment_list)
    """
    if not equipment:
        return False, "Equipment list cannot be empty", []
    
    if not isinstance(equipment, list):
        return False, "Equipment must be a list", []
    
    normalized = []
    invalid = []
    
    for item in equipment:
        if not isinstance(item, str):
            invalid.append(str(item))
            continue
        
        item_lower = item.strip().lower()
        if not item_lower:
            continue
        
        # Check if equipment is in allowed list (case-insensitive)
        if any(item_lower == allowed.lower() for allowed in ALLOWED_EQUIPMENT):
            normalized.append(item.strip())
        else:
            # Allow custom equipment but log it
            logger.warning(f"Custom equipment name detected: {item}")
            normalized.append(item.strip())  # Allow it but warn
    
    if invalid:
        return False, f"Invalid equipment items (must be strings): {invalid}", []
    
    if not normalized:
        return False, "No valid equipment items found", []
    
    return True, None, normalized


def validate_location(location: str) -> Tuple[bool, Optional[str]]:
    """
    Validate location string.
    Accepts addresses, city names, or lat/lng coordinates.
    Returns (is_valid, error_message)
    """
    if not location or not location.strip():
        return False, "Location cannot be empty"
    
    location = location.strip()
    
    # Check if it's lat/lng format (e.g., "40.7128, -74.0060" or "40.7128,-74.0060")
    lat_lng_pattern = r'^-?\d+\.?\d*,\s*-?\d+\.?\d*$'
    if re.match(lat_lng_pattern, location):
        parts = location.split(',')
        try:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            if not (-90 <= lat <= 90):
                return False, "Latitude must be between -90 and 90"
            if not (-180 <= lng <= 180):
                return False, "Longitude must be between -180 and 180"
            return True, None
        except ValueError:
            return False, "Invalid latitude/longitude format"
    
    # Check if it's a reasonable address/place name (at least 2 characters)
    if len(location) < 2:
        return False, "Location must be at least 2 characters"
    
    if len(location) > 200:
        return False, "Location must be less than 200 characters"
    
    # Address/place name is valid
    return True, None


def validate_workout_id(workout_id: Any) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate workout ID.
    Returns (is_valid, error_message, workout_id_int)
    """
    try:
        workout_id_int = int(workout_id)
        if workout_id_int <= 0:
            return False, "Workout ID must be a positive integer", None
        return True, None, workout_id_int
    except (ValueError, TypeError):
        return False, f"Invalid workout ID: {workout_id}. Must be a positive integer", None

