"""Equipment Detection MCP Server for ROAMFIT."""
import sys
import os
import base64
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from agents.equipment_detection import detect_equipment

mcp = FastMCP("equipment_detection")


@mcp.tool()
async def detect_equipment_tool(
    image_base64: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect equipment from base64 encoded image.
    
    Args:
        image_base64: Base64 encoded image string (with or without data URI prefix)
        location: Optional location string
    
    Returns:
        Dict with equipment list, detection_id, and image_path
    """
    # Remove data URI prefix if present
    if image_base64.startswith("data:image"):
        image_base64 = image_base64.split(",")[1]
    
    # Decode base64 to bytes
    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        return {
            "error": f"Failed to decode base64 image: {str(e)}",
            "equipment": [],
            "detection_id": None
        }
    
    # Save to temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(image_data)
            image_path = tmp_file.name
        
        # Call the existing detect_equipment function
        result = detect_equipment(image_path, location=location)
        
        # Clean up temp file
        Path(image_path).unlink(missing_ok=True)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if 'image_path' in locals():
            Path(image_path).unlink(missing_ok=True)
        return {
            "error": f"Equipment detection failed: {str(e)}",
            "equipment": [],
            "detection_id": None
        }


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Equipment Detection MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()

