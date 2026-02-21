"""
LangGraph agent for flight disruption recovery.

Nodes:
- intent_extractor: Determine if user is searching or in recovery mode
- sql_generator_node: Build SQL query
- db_query_node: Execute database query
- ranking_node: Score and rank flights
- response_generator_node: Format response for UI
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from sql_generator import SQLQueryBuilder
from ranking_engine import RankingEngine
from utils import risk_label, calculate_weather_score, format_flight_display, parse_flight_id_from_input

logger = logging.getLogger(__name__)


class FlightAgentState:
    """State holder for agent workflow."""
    
    def __init__(self):
        self.user_input = ""
        self.intent = None
        self.extracted_flight_id = None
        self.search_params = {}
        self.query_results = []
        self.ranked_flights = []
        self.response = ""
        self.explanation = {}


class FlightDisruptionAgent:
    """LangGraph-like agent for flight recovery."""
    
    def __init__(self, db_path: str = "flights.db"):
        """
        Initialize agent.
        
        Args:
            db_path: Path to SQLite database
        """
        self.sql_builder = SQLQueryBuilder(db_path)
        self.ranking_engine = RankingEngine()
        self.state = FlightAgentState()
    
    def intent_extractor(self, user_input: str) -> Dict[str, Any]:
        """
        Extract user intent from input.
        
        Returns either:
        - intent="recovery" with flight_id
        - intent="search" with search parameters
        
        Args:
            user_input: Raw user input text
            
        Returns:
            State dict with intent and extracted info
        """
        user_lower = user_input.lower()
        state = {
            "user_input": user_input,
            "intent": None,
            "extracted_flight_id": None,
            "search_params": {}
        }
        
        # Check for recovery intent (cancelled flight)
        if any(kw in user_lower for kw in ["cancelled", "canceled", "disrupted", "alternatives for", "find alternatives"]):
            state["intent"] = "recovery"
            
            # Extract flight ID
            flight_id = parse_flight_id_from_input(user_input)
            if flight_id:
                state["extracted_flight_id"] = flight_id
                return state
        
        # Check for direct flight ID in disruption mode
        flight_id = parse_flight_id_from_input(user_input)
        if flight_id and len(user_input.split()) <= 3:  # Short input like "AI203"
            state["intent"] = "recovery"
            state["extracted_flight_id"] = flight_id
            return state
        
        # Default to search intent
        state["intent"] = "search"
        state["search_params"] = self._extract_search_params(user_input)
        
        return state
    
    def _extract_search_params(self, user_input: str) -> Dict[str, Any]:
        """
        Extract search parameters from natural language.
        
        Args:
            user_input: User's search query
            
        Returns:
            Dictionary with source, destination, date, etc.
        """
        params = {}
        user_lower = user_input.lower()
        
        # Simple heuristic-based extraction
        city_aliases = {
            "delhi": "Delhi",
            "mumbai": "Mumbai",
            "bombay": "Mumbai",
            "chennai": "Chennai",
            "madras": "Chennai",
            "bangalore": "Bangalore",
            "hyderabad": "Hyderabad",
            "kolkata": "Kolkata",
            "pune": "Pune",
            "ahmedabad": "Ahmedabad",
            "jaipur": "Jaipur",
            "lucknow": "Lucknow",
            "kochi": "Kochi",
            "indore": "Indore",
            "chandigarh": "Chandigarh",
            "goa": "Goa",
            "visakhapatnam": "Visakhapatnam",
        }
        
        words = user_lower.split()
        found_cities = []
        
        for word in words:
            for key, value in city_aliases.items():
                if key in word:
                    found_cities.append(value)
        
        if len(found_cities) >= 2:
            params["source"] = found_cities[0]
            params["destination"] = found_cities[1]
        elif len(found_cities) == 1:
            params["destination"] = found_cities[0]
        
        # Extract time preferences
        if any(kw in user_lower for kw in ["night", "late night", "midnight"]):
            params["time_label"] = "night"
        elif any(kw in user_lower for kw in ["afternoon", "12", "13", "14", "15", "16", "17"]):
            params["departure_window"] = ("12:00", "18:00")
            params["time_label"] = "afternoon"
        elif any(kw in user_lower for kw in ["morning", "6", "7", "8", "9", "10", "11"]):
            params["departure_window"] = ("06:00", "12:00")
            params["time_label"] = "morning"
        elif any(kw in user_lower for kw in ["evening", "18", "19", "20", "21"]):
            params["departure_window"] = ("18:00", "22:00")
            params["time_label"] = "evening"
        
        # Extract date preferences
        if "tomorrow" in user_lower:
            params["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in user_lower:
            params["date"] = datetime.now().strftime("%Y-%m-%d")
        
        return params
    
    def db_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database query based on intent.
        
        Args:
            state: Current agent state
            
        Returns:
            State with query_results added
        """
        intent = state.get("intent")
        
        if intent == "recovery":
            # Recovery flow: fetch original and alternatives
            flight_id = state.get("extracted_flight_id")
            
            if not flight_id:
                state["query_results"] = []
                state["response"] = "❌ Could not identify flight ID. Please provide flight ID (e.g., AI203)"
                return state
            
            # Fetch original flight
            original = self.sql_builder.get_flight_by_id(flight_id)
            
            if not original:
                state["query_results"] = []
                state["response"] = f"❌ Flight {flight_id} not found in system."
                return state
            
            if original.get("status") != "Cancelled":
                state["query_results"] = [original]
                state["response"] = f"ℹ️ Flight {flight_id} is {original.get('status')}. No recovery needed."
                return state
            
            # Find alternatives
            alternatives = self.sql_builder.get_alternative_flights(original, max_results=10)
            
            # If no same-route alternatives, show best alternatives from same airports with discount
            if not alternatives:
                source = original.get("source")
                destination = original.get("destination")
                # Get any active flights from that source to nearby destinations
                alternatives = self.sql_builder.search_flights(
                    source=source,
                    status="Active"
                )[:10]
            
            state["query_results"] = alternatives
            state["original_flight"] = original
            
        else:  # search intent
            search_params = state.get("search_params", {})
            params = dict(search_params)
            time_label = params.pop("time_label", None)
            date_value = params.get("date")
            fallback_note = ""

            if time_label == "night":
                night_params_late = dict(params)
                night_params_late["departure_window"] = ("22:00", "23:59")
                night_params_early = dict(params)
                night_params_early["departure_window"] = ("00:00", "06:00")
                results = self.sql_builder.search_flights(**night_params_late)
                results += self.sql_builder.search_flights(**night_params_early)
                results_by_id = {f["flight_id"]: f for f in results}
                results = list(results_by_id.values())
            else:
                results = self.sql_builder.search_flights(**params)

            if not results and time_label == "night":
                params["departure_window"] = ("18:00", "22:00")
                results = self.sql_builder.search_flights(**params)
                if results:
                    fallback_note = "🌙 Night flights are not available. Showing evening flights instead."

            if not results and date_value:
                try:
                    date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                    next_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
                except Exception:
                    next_date = date_value

                params["date"] = next_date
                if time_label == "night":
                    if "departure_window" not in params:
                        params["departure_window"] = ("18:00", "22:00")
                    results = self.sql_builder.search_flights(**params)
                else:
                    results = self.sql_builder.search_flights(**params)

                if results:
                    if fallback_note:
                        fallback_note += " "
                    fallback_note += f"📅 No flights on {date_value}. Showing flights on {next_date} instead."

            state["query_results"] = results
            state["fallback_note"] = fallback_note
        
        return state
    
    def ranking_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank flights using ranking engine.
        
        Args:
            state: Current agent state
            
        Returns:
            State with ranked_flights added
        """
        flights = state.get("query_results", [])
        
        if not flights:
            state["ranked_flights"] = []
            return state
        
        ranked = self.ranking_engine.rank_flights(flights, top_n=3)
        state["ranked_flights"] = ranked
        
        # Store explanations
        explanations = {}
        for flight, score in ranked:
            explanations[flight["flight_id"]] = self.ranking_engine.generate_explanation(flight, score)
        state["explanations"] = explanations
        
        return state
    
    def response_generator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final response for UI.
        
        Args:
            state: Current agent state
            
        Returns:
            State with response added
        """
        if state.get("response"):  # Already set in error case
            return state
        
        ranked_flights = state.get("ranked_flights", [])
        intent = state.get("intent")
        
        if not ranked_flights:
            if intent == "recovery":
                state["response"] = "❌ No direct flights available. Showing best connecting options.\n\n(Connecting flights simulation not fully implemented in MVP)"
            else:
                state["response"] = "❌ No flights found matching your criteria. Try different search parameters."
            return state
        
        # Format response
        response_lines = []
        
        if intent == "recovery":
            response_lines.append("🛫 **DISRUPTION RECOVERY MODE**\n")
            original = state.get("original_flight")
            if original:
                response_lines.append(
                    f"Original flight: **{original['flight_id']}** ({original['source']} → {original['destination']}) - CANCELLED\n"
                )
            response_lines.append("**Best alternatives are listed below.**\n")
        else:
            response_lines.append("**Best available flights are listed below.**\n")

        fallback_note = state.get("fallback_note")
        if fallback_note:
            response_lines.append(f"{fallback_note}\n")
        
        state["response"] = "".join(response_lines)
        
        return state
    
    def run(self, user_input: str) -> tuple[str, List[Dict]]:
        """
        Execute the full agent workflow.
        
        Args:
            user_input: User's text input
            
        Returns:
            (response_text, ranked_flights)
        """
        # Step 1: Extract intent
        state = self.intent_extractor(user_input)
        
        # Step 2: Query database
        state = self.db_query_node(state)
        
        # Step 3: Rank results
        state = self.ranking_node(state)
        
        # Step 4: Generate response
        state = self.response_generator_node(state)
        
        ranked = state.get("ranked_flights", [])
        response = state.get("response", "")
        
        return response, ranked


if __name__ == "__main__":
    agent = FlightDisruptionAgent()
    
    # Test recovery flow
    print("TEST 1: Recovery mode")
    response, ranked = agent.run("My flight AI203 got cancelled")
    print(response)
    
    # Test search flow
    print("\n\nTEST 2: Search flights")
    response, ranked = agent.run("Show flights from Delhi to Pune tomorrow afternoon")
    print(response)
