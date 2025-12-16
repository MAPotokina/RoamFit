"""Graph/Trends MCP Server for ROAMFIT."""
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP

from agents.graph_trends import generate_charts, get_workout_stats

mcp = FastMCP("graph_trends")


@mcp.tool()
async def get_workout_stats_tool() -> Dict[str, Any]:
    """
    Get workout statistics from database.

    Returns:
        Dict with total_workouts, completed_workouts, recent_workouts_30_days,
        workouts_per_week, and completion_rate
    """
    return get_workout_stats()


@mcp.tool()
async def generate_charts_tool(chart_type: str = "frequency") -> Dict[str, str]:
    """
    Generate workout progress charts.

    Args:
        chart_type: Type of chart ("frequency" or "equipment", default: "frequency")

    Returns:
        Dict with chart_type, image_base64, and format
    """
    return generate_charts(chart_type=chart_type)


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Graph/Trends MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
