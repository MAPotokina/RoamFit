"""Workout Generator MCP Server for ROAMFIT."""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from agents.workout_generator import generate_workout

mcp = FastMCP("workout_generator")


@mcp.tool()
async def generate_workout_tool(
    equipment: List[str],
    workout_history: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate workout plan based on equipment and history.
    
    Args:
        equipment: List of equipment names (e.g., ["dumbbells", "bench"])
        workout_history: Optional dict with workout history summary
    
    Returns:
        Dict with workout plan (exercises, duration, focus, etc.)
    """
    return generate_workout(equipment=equipment, workout_history=workout_history)


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Workout Generator MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()

