"""
Flight ranking engine with explainability.

Implements the scoring formula:
score = (0.35 * seat_score) + (0.25 * time_score) + (0.20 * weather_score_adj) 
        + (0.10 * congestion_score) + (0.10 * reliability_score)
"""

from typing import List, Dict, Tuple
from utils import (
    calculate_weather_score,
    risk_label,
    time_preference_score,
    normalize_seats_score
)


class RankingEngine:
    """Score and rank flights based on multiple factors."""
    
    # Weighting constants
    SEAT_WEIGHT = 0.35
    TIME_WEIGHT = 0.25
    WEATHER_WEIGHT = 0.20
    CONGESTION_WEIGHT = 0.10
    RELIABILITY_WEIGHT = 0.10
    
    def __init__(self):
        """Initialize ranking engine."""
        pass
    
    def calculate_seat_score(self, seats_available: int) -> float:
        """
        Score based on available seats (0-1).
        More seats = higher score.
        
        Args:
            seats_available: Number of available seats
            
        Returns:
            Seat score (0-1)
        """
        return normalize_seats_score(seats_available)
    
    def calculate_time_score(self, departure_time: str) -> float:
        """
        Score based on departure time preference.
        Afternoon (12-17) preferred.
        
        Args:
            departure_time: Time in HH:MM format
            
        Returns:
            Time score (0-1)
        """
        return time_preference_score(departure_time)
    
    def calculate_weather_score_adj(
        self,
        fog_risk: float,
        rain_risk: float,
        wind_risk: float
    ) -> float:
        """
        Score based on weather (inverse of risk).
        Lower weather risk = higher score.
        
        Args:
            fog_risk: Fog risk (0-1)
            rain_risk: Rain risk (0-1)
            wind_risk: Wind risk (0-1)
            
        Returns:
            Weather score (0-1)
        """
        weather_risk = calculate_weather_score(fog_risk, rain_risk, wind_risk)
        return 1.0 - weather_risk  # Invert: low risk = high score
    
    def calculate_congestion_score(self, airport_congestion: float) -> float:
        """
        Score based on airport congestion (inverse).
        Lower congestion = higher score.
        
        Args:
            airport_congestion: Congestion level (0-1)
            
        Returns:
            Congestion score (0-1)
        """
        return 1.0 - airport_congestion
    
    def calculate_reliability_score(self, delay_probability: float) -> float:
        """
        Score based on reliability (inverse of delay probability).
        Lower delay probability = higher score.
        
        Args:
            delay_probability: Probability of delay (0-1)
            
        Returns:
            Reliability score (0-1)
        """
        return 1.0 - delay_probability
    
    def rank_flights(self, flights: List[Dict], top_n: int = 3) -> List[Tuple[Dict, float]]:
        """
        Rank flights and return top N with scores.
        
        Args:
            flights: List of flight records
            top_n: Number of top flights to return
            
        Returns:
            List of (flight, score) tuples, sorted by score descending
        """
        if not flights:
            return []
        
        scored_flights = []
        
        for flight in flights:
            seat_score = self.calculate_seat_score(flight.get("seats_available", 0))
            time_score = self.calculate_time_score(flight.get("departure_time", "12:00"))
            weather_score = self.calculate_weather_score_adj(
                flight.get("fog_risk", 0),
                flight.get("rain_risk", 0),
                flight.get("wind_risk", 0)
            )
            congestion_score = self.calculate_congestion_score(
                flight.get("airport_congestion", 0)
            )
            reliability_score = self.calculate_reliability_score(
                flight.get("delay_probability", 0)
            )
            
            # Calculate weighted total score
            total_score = (
                (self.SEAT_WEIGHT * seat_score) +
                (self.TIME_WEIGHT * time_score) +
                (self.WEATHER_WEIGHT * weather_score) +
                (self.CONGESTION_WEIGHT * congestion_score) +
                (self.RELIABILITY_WEIGHT * reliability_score)
            )
            
            scored_flights.append((flight, total_score))
        
        # Sort by score descending, return top N
        scored_flights.sort(key=lambda x: x[1], reverse=True)
        return scored_flights[:top_n]
    
    def generate_explanation(self, flight: Dict, score: float) -> str:
        """
        Generate human-readable explanation for why a flight was ranked.
        
        Args:
            flight: Flight record
            score: Flight's calculated score
            
        Returns:
            Explanation string
        """
        factors = []
        
        # Analyze each component
        seat_score = self.calculate_seat_score(flight.get("seats_available", 0))
        if seat_score > 0.7:
            factors.append("excellent seat availability")
        elif seat_score > 0.4:
            factors.append("good seat availability")
        
        time_score = self.calculate_time_score(flight.get("departure_time", "12:00"))
        if time_score > 0.7:
            factors.append("optimal afternoon timing")
        elif time_score > 0.4:
            factors.append("good departure time")
        
        weather_score = self.calculate_weather_score_adj(
            flight.get("fog_risk", 0),
            flight.get("rain_risk", 0),
            flight.get("wind_risk", 0)
        )
        if weather_score > 0.7:
            factors.append("low weather risk")
        elif weather_score > 0.4:
            factors.append("acceptable weather conditions")
        
        congestion_score = self.calculate_congestion_score(
            flight.get("airport_congestion", 0)
        )
        if congestion_score > 0.7:
            factors.append("low airport congestion")
        
        reliability_score = self.calculate_reliability_score(
            flight.get("delay_probability", 0)
        )
        if reliability_score > 0.7:
            factors.append("high on-time reliability")
        elif reliability_score > 0.4:
            factors.append("good reliability track record")
        
        if not factors:
            return "Selected as one of the best available options."
        
        return "Selected due to " + ", ".join(factors) + "."


if __name__ == "__main__":
    engine = RankingEngine()
    
    # Test data
    test_flights = [
        {
            "flight_id": "AI101",
            "source": "Delhi",
            "destination": "Mumbai",
            "seats_available": 45,
            "departure_time": "14:30",
            "fog_risk": 0.1,
            "rain_risk": 0.2,
            "wind_risk": 0.15,
            "airport_congestion": 0.4,
            "delay_probability": 0.2
        },
        {
            "flight_id": "SG202",
            "source": "Delhi",
            "destination": "Mumbai",
            "seats_available": 5,
            "departure_time": "06:00",
            "fog_risk": 0.5,
            "rain_risk": 0.3,
            "wind_risk": 0.4,
            "airport_congestion": 0.8,
            "delay_probability": 0.6
        }
    ]
    
    print("Ranking test flights:")
    ranked = engine.rank_flights(test_flights)
    for flight, score in ranked:
        print(f"\n{flight['flight_id']}: Score {score:.3f}")
        explanation = engine.generate_explanation(flight, score)
        print(f"  {explanation}")
