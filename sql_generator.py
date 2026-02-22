"""
Safe SQL query builder with parameterized queries to prevent SQL injection.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from utils import calculate_weather_score

class SQLQueryBuilder:
    """Build safe parameterized SQL queries for flight searches."""
    
    def __init__(self, db_path: str = "flights.db"):
        """
        Initialize query builder.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def search_flights(
        self,
        source: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
        departure_window: Optional[Tuple[str, str]] = None,
        exclude_flight_id: Optional[str] = None,
        status: str = "Active",
        mobility_friendly: Optional[bool] = None,
        data_source: Optional[str] = None
    ) -> List[Dict]:
        """
        Search flights with optional filters.
        
        Args:
            source: Origin city
            destination: Destination city
            date: Flight date (YYYY-MM-DD)
            departure_window: Tuple (start_time, end_time) in HH:MM format
            exclude_flight_id: Flight ID to exclude (for recovery flows)
            status: Flight status (default "Active")
            mobility_friendly: Filter by mobility-friendliness (True = YES, False = NO, None = no filter)
            data_source: Filter by data source ('fake', 'opensky', None for all)
            
        Returns:
            List of matching flight records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM flights WHERE 1=1"
        params = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if destination:
            # For OpenSky data, most destinations are "Unknown", so make it optional
            query += " AND (destination = ? OR destination = 'Unknown')"
            params.append(destination)
        
        if date:
            query += " AND date = ?"
            params.append(date)
        
        if departure_window:
            start_time, end_time = departure_window
            query += " AND departure_time BETWEEN ? AND ?"
            params.extend([start_time, end_time])
        
        if exclude_flight_id:
            query += " AND flight_id != ?"
            params.append(exclude_flight_id)
        
        if mobility_friendly is not None:
            mobility_value = "YES" if mobility_friendly else "NO"
            query += " AND mobility_friendly = ?"
            params.append(mobility_value)
        
        if data_source is not None:
            query += " AND data_source = ?"
            params.append(data_source)
        
        query += " AND status = ?"
        params.append(status)
        
        query += " ORDER BY departure_time ASC"
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return []
    
    def get_flight_by_id(self, flight_id: str) -> Optional[Dict]:
        """
        Get single flight by ID.
        
        Args:
            flight_id: Flight identifier
            
        Returns:
            Flight record or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return None
    
    def get_alternative_flights(
        self,
        original_flight: Dict,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Get alternative flights for a cancelled/disrupted flight.
        
        Args:
            original_flight: The original flight record
            max_results: Maximum flights to return
            
        Returns:
            List of alternative flights (same route, same/next day)
        """
        from datetime import datetime, timedelta
        
        source = original_flight.get("source")
        destination = original_flight.get("destination")
        original_date = original_flight.get("date")
        
        # Calculate next day date
        try:
            date_obj = datetime.strptime(original_date, "%Y-%m-%d")
            next_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        except:
            next_date = original_date
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get flights from same source->destination, same day or next day
        query = """
        SELECT * FROM flights
        WHERE source = ? AND destination = ?
          AND date IN (?, ?)
          AND status = 'Active'
          AND flight_id != ?
        ORDER BY departure_time ASC
        LIMIT ?
        """
        
        try:
            cursor.execute(
                query,
                (source, destination, original_date, next_date,
                 original_flight.get("flight_id"), max_results)
            )
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return []


if __name__ == "__main__":
    builder = SQLQueryBuilder()
    
    # Test searches
    print("Test 1: Get flights from Delhi to Pune")
    results = builder.search_flights(source="Delhi", destination="Pune")
    print(f"Found {len(results)} flights")
    
    print("\nTest 2: Get flights with departure time window")
    results = builder.search_flights(
        source="Mumbai",
        destination="Bangalore",
        departure_window=("12:00", "18:00")
    )
    print(f"Found {len(results)} flights in afternoon (12-18)")
