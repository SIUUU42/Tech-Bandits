"""
Utility functions for the Flight Disruption Recovery Assistant.
"""

import re

def risk_label(score: float) -> str:
    """
    Convert numeric risk score (0-1) to UI label.
    
    Args:
        score: Risk value between 0 and 1
        
    Returns:
        "Low", "Medium", or "High"
    """
    if score < 0.3:
        return "Low"
    elif score < 0.6:
        return "Medium"
    else:
        return "High"


def calculate_weather_score(fog_risk: float, rain_risk: float, wind_risk: float) -> float:
    """
    Calculate average weather risk score.
    
    Args:
        fog_risk: Fog risk (0-1)
        rain_risk: Rain risk (0-1)
        wind_risk: Wind risk (0-1)
        
    Returns:
        Average weather score (0-1)
    """
    return (fog_risk + rain_risk + wind_risk) / 3


def format_flight_display(flight: dict) -> str:
    """
    Format flight data for UI display.
    
    Args:
        flight: Flight record from database
        
    Returns:
        Formatted flight string
    """
    flight_id = flight.get("flight_id", "N/A")
    airline = flight.get("airline", "N/A")
    source = flight.get("source", "N/A")
    destination = flight.get("destination", "N/A")
    departure_time = flight.get("departure_time", "N/A")
    seats_available = flight.get("seats_available", 0)
    weather_score = calculate_weather_score(
        flight.get("fog_risk", 0),
        flight.get("rain_risk", 0),
        flight.get("wind_risk", 0)
    )
    weather_label = risk_label(weather_score)
    delay_label = risk_label(flight.get("delay_probability", 0))
    price = flight.get("price", 0)
    
    seats_category = "Plenty" if seats_available > 30 else "Limited" if seats_available > 10 else "Scarce"
    
    return f"""
**✈️  {flight_id}** ({airline}) — {source} → {destination} — {departure_time}
- **Seats:** {seats_available} ({seats_category})
- **Weather Risk:** {weather_label}
- **Delay Risk:** {delay_label}
- **Price:** ₹{price}
"""


def parse_flight_id_from_input(user_input: str) -> str:
    """
    Extract flight ID from user input.
    
    Args:
        user_input: User's text input
        
    Returns:
        Flight ID if found, else empty string
    """
    match = re.search(r"\b[A-Za-z0-9]{2,3}\d{2,4}\b", user_input)
    if match:
        return match.group(0).upper()
    return ""


def time_preference_score(departure_time: str) -> float:
    """
    Score departure time (afternoon 12-17 preferred).
    
    Args:
        departure_time: Time in HH:MM format
        
    Returns:
        Score between 0 and 1
    """
    try:
        hour = int(departure_time.split(":")[0])
        # Prefer afternoon (12-17)
        if 12 <= hour <= 17:
            return 1.0 - (abs(hour - 14.5) / 5.5)  # Peak at 14:30
        elif 7 <= hour < 12:
            return 0.5 + (hour - 7) / 10  # Morning: ramping up
        elif 18 <= hour < 22:
            return 0.5 - ((hour - 18) / 4)  # Evening: ramping down
        else:
            return 0.2  # Night flights not preferred
    except:
        return 0.5


def normalize_seats_score(seats_available: int, max_seats: int = 100) -> float:
    """
    Normalize seats count to 0-1 score.
    
    Args:
        seats_available: Number of available seats
        max_seats: Maximum seats for normalization (default 100)
        
    Returns:
        Normalized score between 0 and 1
    """
    return min(1.0, seats_available / max_seats)
