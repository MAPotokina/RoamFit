"""Location Activity MCP Server for ROAMFIT."""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from agents.location_activity import find_nearby_gyms, find_running_tracks

mcp = FastMCP("location_activity")


@mcp.tool()
async def find_nearby_gyms_tool(
    location: str,
    radius_km: float = 2.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find nearby gyms from location.
    
    Args:
        location: Location string (address, city, etc.)
        radius_km: Search radius in kilometers (default: 2.0)
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of gyms with name, address, distance, coordinates
    """
    return find_nearby_gyms(location=location, radius_km=radius_km, limit=limit)


@mcp.tool()
async def find_running_tracks_tool(
    location: str,
    radius_km: float = 2.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find nearby running tracks, parks, and trails.
    
    Args:
        location: Location string (address, city, etc.)
        radius_km: Search radius in kilometers (default: 2.0)
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of locations with name, address, distance, coordinates
    """
    return find_running_tracks(location=location, radius_km=radius_km, limit=limit)


def main() -> None:
    """Run the MCP server on stdio."""
    print("Starting Location Activity MCP server on stdio...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()

