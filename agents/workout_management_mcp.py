"""Workout Management MCP Server for ROAMFIT."""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from agents.workout_management import (
    list_workouts,
    get_workout,
    edit_workout,
    remove_workout,
    mark_workout_complete
)

mcp = FastMCP("workout_management")


@mcp.tool()
async def list_workouts_tool(limit: int = 10) -> List[Dict[str, Any]]:
    """
    List recent workouts.
    
    Args:
        limit: Maximum number of workouts to return (default: 10)
    
    Returns:
        List of workout dictionaries
    """
    return list_workouts(limit=limit)


@mcp.tool()
async def get_workout_tool(workout_id: int) -> Dict[str, Any]:
    """
    Get workout by ID.
    
    Args:
        workout_id: The workout ID to retrieve
    
    Returns:
        Workout dictionary or None if not found
    """
    workout = get_workout(workout_id)
    if workout:
        return workout
    else:
        return {"error": f"Workout #{workout_id} not found"}


@mcp.tool()
async def edit_workout_tool(
    workout_id: int,
    equipment: Optional[List[str]] = None,
    location: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Edit workout fields.
    
    Args:
        workout_id: The workout ID to edit
        equipment: Optional list of equipment to update
        location: Optional location string to update
        completed: Optional completion status (True/False) to update
    
    Returns:
        Dict with success status and message
    """
    return edit_workout(
        workout_id=workout_id,
        equipment=equipment,
        location=location,
        completed=completed
    )


@mcp.tool()
async def delete_workout_tool(workout_id: int) -> Dict[str, Any]:
    """
    Delete workout by ID.
    
    Args:
        workout_id: The workout ID to delete
    
    Returns:
        Dict with success status and message
    """
    return remove_workout(workout_id)


@mcp.tool()
async def mark_workout_complete_tool(workout_id: int, completed: bool = True) -> Dict[str, Any]:
    """
    Mark workout as completed or incomplete.
    
    Args:
        workout_id: The workout ID
        completed: True to mark as completed, False to mark as incomplete
    
    Returns:
        Dict with success status and message
    """
    return mark_workout_complete(workout_id, completed)


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Workout Management MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()

