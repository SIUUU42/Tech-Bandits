"""
OpenSky Network API provider for live flight data.

API Documentation: https://openskynetwork.github.io/opensky-api/rest.html
No authentication required for public endpoint (rate-limited).
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Tuple
from datetime import datetime


# India bounding box (approximate)
INDIA_BBOX = {
    "lamin": 6.5,    # Southern latitude
    "lomin": 68.0,   # Western longitude
    "lamax": 35.5,   # Northern latitude
    "lomax": 97.5    # Eastern longitude
}


def fetch_states(bbox: Optional[Dict[str, float]] = None, timeout: int = 10) -> List[Dict]:
    """
    Fetch current aircraft states from OpenSky Network API.
    
    Args:
        bbox: Optional bounding box dict with keys: lamin, lomin, lamax, lomax
        timeout: Request timeout in seconds
        
    Returns:
        List of normalized plane state dictionaries
        
    Raises:
        Exception: If API call fails (caller should handle gracefully)
    """
    base_url = "https://opensky-network.org/api/states/all"
    
    # Build URL with bounding box if provided
    if bbox:
        params = f"?lamin={bbox['lamin']}&lomin={bbox['lomin']}&lamax={bbox['lamax']}&lomax={bbox['lomax']}"
        url = base_url + params
    else:
        url = base_url
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'FlightDisruptionAssistant/1.0')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # Parse the response
        # OpenSky returns: {"time": timestamp, "states": [ [field1, field2, ...], ... ]}
        if not data or "states" not in data or not data["states"]:
            return []
        
        normalized_planes = []
        
        for state in data["states"]:
            # State array indices (from OpenSky docs):
            # 0: icao24, 1: callsign, 2: origin_country, 3: time_position, 
            # 4: last_contact, 5: longitude, 6: latitude, 7: baro_altitude,
            # 8: on_ground, 9: velocity, 10: true_track, 11: vertical_rate,
            # 12: sensors, 13: geo_altitude, 14: squawk, 15: spi, 16: position_source
            
            plane = {
                "icao24": state[0] or "",
                "callsign": (state[1] or "").strip(),
                "origin_country": state[2] or "Unknown",
                "time_position": state[3],
                "last_contact": state[4],
                "longitude": state[5],
                "latitude": state[6],
                "baro_altitude": state[7],
                "on_ground": state[8] or False,
                "velocity": state[9],
                "true_track": state[10],
                "vertical_rate": state[11],
                "geo_altitude": state[13] if len(state) > 13 else None,
            }
            
            normalized_planes.append(plane)
        
        return normalized_planes
    
    except urllib.error.HTTPError as e:
        raise Exception(f"OpenSky API HTTP error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"OpenSky API connection error: {e.reason}")
    except json.JSONDecodeError as e:
        raise Exception(f"OpenSky API response parsing error: {e}")
    except Exception as e:
        raise Exception(f"OpenSky API unexpected error: {e}")


def fetch_india_flights(timeout: int = 10) -> List[Dict]:
    """
    Fetch aircraft states within India's airspace.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        List of normalized plane state dictionaries
    """
    return fetch_states(bbox=INDIA_BBOX, timeout=timeout)


def infer_airline_from_callsign(callsign: str) -> str:
    """
    Attempt to infer airline name from callsign prefix.
    
    Args:
        callsign: Aircraft callsign (e.g., "AI203", "UAE512")
        
    Returns:
        Airline name or origin country
    """
    if not callsign:
        return "Unknown"
    
    # Common Indian airline prefixes
    airline_map = {
        "AI": "Air India",
        "AIC": "Air India",
        "SG": "SpiceJet",
        "SGJ": "SpiceJet",
        "6E": "IndiGo",
        "IGO": "IndiGo",
        "UK": "Vistara",
        "VTI": "Vistara",
        "9I": "Alliance Air",
        "G8": "GoAir",
        "GES": "GoAir",
        "I5": "AirAsia India",
    }
    
    # Check first 2-3 characters
    for prefix, airline in airline_map.items():
        if callsign.upper().startswith(prefix):
            return airline
    
    return "Unknown Airline"


def infer_nearest_city(lat: float, lon: float) -> Tuple[str, str]:
    """
    Infer nearest major Indian city based on coordinates and predict destination.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Tuple of (source_city, destination_city) based on current location
    """
    # Major Indian city coordinates (approximate)
    cities = {
        "Delhi": (28.7041, 77.1025),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
        "Ahmedabad": (23.0225, 72.5714),
        "Jaipur": (26.9124, 75.7873),
    }
    
    # Common routes (source -> destination pairs)
    common_routes = {
        "Delhi": ["Mumbai", "Bangalore", "Hyderabad", "Pune"],
        "Mumbai": ["Delhi", "Bangalore", "Chennai", "Hyderabad"],
        "Bangalore": ["Delhi", "Mumbai", "Chennai", "Hyderabad"],
        "Chennai": ["Delhi", "Mumbai", "Bangalore", "Hyderabad"],
        "Hyderabad": ["Delhi", "Mumbai", "Bangalore", "Chennai"],
        "Kolkata": ["Delhi", "Mumbai", "Bangalore"],
        "Pune": ["Delhi", "Mumbai", "Bangalore", "Chennai"],
        "Ahmedabad": ["Delhi", "Mumbai", "Bangalore"],
        "Jaipur": ["Delhi", "Mumbai", "Bangalore"],
    }
    
    if lat is None or lon is None:
        return ("Unknown", "Unknown")
    
    # Find closest city (simple distance calculation)
    min_distance = float('inf')
    closest_city = "Unknown"
    
    for city, (city_lat, city_lon) in cities.items():
        # Simple Euclidean distance (not geographically accurate but good enough)
        distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_city = city
    
    # Predict destination from common routes
    destination = "Unknown"
    if closest_city in common_routes:
        # Use first common destination (could be randomized for variety)
        destination = common_routes[closest_city][0]
    
    return (closest_city, destination)


if __name__ == "__main__":
    # Test the OpenSky API
    print("Testing OpenSky Network API...")
    print(f"Fetching aircraft over India: {INDIA_BBOX}")
    
    try:
        planes = fetch_india_flights()
        print(f"✅ Found {len(planes)} aircraft")
        
        if planes:
            print("\nSample aircraft:")
            for plane in planes[:3]:
                print(f"  - {plane['callsign'] or plane['icao24']}: "
                      f"{plane['origin_country']} @ "
                      f"({plane['latitude']:.2f}, {plane['longitude']:.2f}) "
                      f"{'on ground' if plane['on_ground'] else 'in flight'}")
    except Exception as e:
        print(f"❌ Error: {e}")
