"""Location Activity Agent for ROAMFIT - MCP Server."""
from typing import List, Dict, Any, Optional
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time


def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Geocode a location string to coordinates."""
    try:
        geolocator = Nominatim(user_agent="roamfit_app")
        location_data = geolocator.geocode(location, timeout=10)
        
        if location_data:
            return {
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "address": location_data.address
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def find_nearby_places(
    location: str,
    place_type: str,
    radius_km: float = 2.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find nearby places using Nominatim search.
    
    Args:
        location: Location string (address, city, etc.)
        place_type: Type of place ("gym", "park", "running track", etc.)
        radius_km: Search radius in kilometers
        limit: Maximum number of results
    
    Returns:
        List of places with name, address, distance
    """
    # Geocode the location
    coords = geocode_location(location)
    if not coords:
        return []
    
    base_lat = coords["latitude"]
    base_lon = coords["longitude"]
    base_point = (base_lat, base_lon)
    
    # Search for places
    geolocator = Nominatim(user_agent="roamfit_app")
    
    try:
        # Construct search query
        query = f"{place_type} near {location}"
        results = geolocator.geocode(query, exactly_one=False, limit=limit * 2)
        
        if not results:
            return []
        
        # Calculate distances and filter by radius
        places = []
        for place in results:
            if place.latitude and place.longitude:
                place_point = (place.latitude, place.longitude)
                distance_km = geodesic(base_point, place_point).kilometers
                
                if distance_km <= radius_km:
                    places.append({
                        "name": place.address.split(",")[0] if place.address else "Unknown",
                        "address": place.address or "Address not available",
                        "latitude": place.latitude,
                        "longitude": place.longitude,
                        "distance_km": round(distance_km, 2),
                        "distance_m": round(distance_km * 1000, 0)
                    })
        
        # Sort by distance and limit results
        places.sort(key=lambda x: x["distance_km"])
        return places[:limit]
        
    except Exception as e:
        print(f"Search error: {e}")
        return []


def find_nearby_gyms(
    location: str,
    radius_km: float = 2.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Find nearby gyms from location."""
    return find_nearby_places(location, "gym", radius_km, limit)


def find_running_tracks(
    location: str,
    radius_km: float = 2.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Find nearby running tracks, parks, and trails."""
    # Search for multiple types
    parks = find_nearby_places(location, "park", radius_km, limit // 2)
    tracks = find_nearby_places(location, "running track", radius_km, limit // 2)
    trails = find_nearby_places(location, "trail", radius_km, limit // 2)
    
    # Combine and deduplicate by address
    all_places = parks + tracks + trails
    seen_addresses = set()
    unique_places = []
    
    for place in all_places:
        addr_key = place["address"]
        if addr_key not in seen_addresses:
            seen_addresses.add(addr_key)
            unique_places.append(place)
    
    # Sort by distance and limit
    unique_places.sort(key=lambda x: x["distance_km"])
    return unique_places[:limit]


# MCP Server setup
try:
    from mcp import Server, Tool
    
    server = Server("location_activity")
    
    @server.tool()
    def find_nearby_gyms_tool(
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
        """
        return find_nearby_gyms(location, radius_km, limit)
    
    @server.tool()
    def find_running_tracks_tool(
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
        """
        return find_running_tracks(location, radius_km, limit)
    
    # Export server for registration
    location_activity_server = server
    
except ImportError:
    # Fallback if MCP not available - just export functions
    location_activity_server = None

