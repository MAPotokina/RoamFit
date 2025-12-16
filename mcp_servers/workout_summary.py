"""Workout Summary MCP Server for ROAMFIT."""
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP

from agents.workout_summary import get_last_workout, summarize_workout_history

mcp = FastMCP("workout_summary")


@mcp.tool()
async def get_last_workout_tool() -> Optional[Dict[str, Any]]:
    """
    Get the most recent workout.

    Returns:
        Dict with workout details or None if no workouts exist
    """
    return get_last_workout()


@mcp.tool()
async def summarize_workout_history_tool(limit: int = 5) -> Dict[str, Any]:
    """
    Summarize recent workout history using LLM.

    Args:
        limit: Number of recent workouts to include (default: 5)

    Returns:
        Dict with summary, last_workout_date, and total_workouts
    """
    return summarize_workout_history(limit=limit)


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Workout Summary MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
