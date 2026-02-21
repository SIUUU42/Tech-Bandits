"""
Database initialization and flight data seeding.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "flights.db"

AIRLINES = [
    ("AI", "Air India"),
    ("SG", "Spice Jet"),
    ("6E", "Indigo"),
]

# Indian cities for realistic flights
INDIAN_CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Kochi", "Indore", "Chandigarh", "Goa", "Visakhapatnam"
]

def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if present (fresh start)
    cursor.execute("DROP TABLE IF EXISTS flights")
    
    # Create flights table with relaxed constraints for API data
    cursor.execute("""
    CREATE TABLE flights (
        flight_id TEXT PRIMARY KEY,
        airline TEXT NOT NULL,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        date TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        seats_available INTEGER DEFAULT 0,
        price INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        fog_risk REAL DEFAULT 0.3,
        rain_risk REAL DEFAULT 0.3,
        wind_risk REAL DEFAULT 0.3,
        airport_congestion REAL DEFAULT 0.5,
        previous_flight_delay REAL DEFAULT 0.2,
        delay_probability REAL DEFAULT 0.4,
        mobility_friendly TEXT NOT NULL DEFAULT 'YES',
        api_provider TEXT,
        api_flight_key TEXT,
        last_updated_utc TEXT,
        raw_json TEXT
    )
    """)
    
    # Create indexes for fast queries
    cursor.execute("CREATE INDEX idx_source ON flights(source)")
    cursor.execute("CREATE INDEX idx_destination ON flights(destination)")
    cursor.execute("CREATE INDEX idx_date ON flights(date)")
    cursor.execute("CREATE INDEX idx_departure_time ON flights(departure_time)")
    cursor.execute("CREATE INDEX idx_status ON flights(status)")
    cursor.execute("CREATE INDEX idx_flight_id ON flights(flight_id)")
    
    conn.commit()
    conn.close()


def generate_flight_id() -> str:
    """Generate realistic Indian airline flight ID."""
    airline = random.choice([code for code, _ in AIRLINES])
    number = str(random.randint(100, 9999))
    return f"{airline}{number}"


def generate_time() -> str:
    """Generate realistic flight time in HH:MM format."""
    hour = random.choice(list(range(6, 22)))
    minute = random.choice([0, 15, 30, 45])
    return f"{hour:02d}:{minute:02d}"


def add_hours_to_time(time_str: str, hours: int) -> str:
    """Add hours to a time string in HH:MM format."""
    try:
        h, m = map(int, time_str.split(":"))
        new_h = (h + hours) % 24
        return f"{new_h:02d}:{m:02d}"
    except:
        return "23:59"


def generate_flights(count: int = 300) -> List[Dict]:
    """
    Generate realistic Indian domestic flight data with focus on 
    Delhi, Mumbai, Pune routes with morning, afternoon, and evening flights.
    
    Args:
        count: Number of flights to generate (default 300)
        
    Returns:
        List of flight dictionaries
    """
    flights = []

    fixed_flights = [
        {
            "flight_id": "AI203",
            "airline": "Air India",
            "source": "Delhi",
            "destination": "Mumbai",
            "date": "2026-02-22",
            "departure_time": "09:00",
            "arrival_time": "11:00",
            "seats_available": 0,
            "price": 5200,
            "status": "Cancelled",
            "fog_risk": 0.3,
            "rain_risk": 0.4,
            "wind_risk": 0.2,
            "airport_congestion": 0.6,
            "previous_flight_delay": 0.2,
            "delay_probability": 0.7,
            "mobility_friendly": "YES",
        },
        {
            "flight_id": "A1203",
            "airline": "Air India",
            "source": "Delhi",
            "destination": "Mumbai",
            "date": "2026-02-22",
            "departure_time": "09:00",
            "arrival_time": "11:00",
            "seats_available": 0,
            "price": 5200,
            "status": "Cancelled",
            "fog_risk": 0.3,
            "rain_risk": 0.4,
            "wind_risk": 0.2,
            "airport_congestion": 0.6,
            "previous_flight_delay": 0.2,
            "delay_probability": 0.7,
            "mobility_friendly": "YES",
        },
        {
            "flight_id": "SG999",
            "airline": "Spice Jet",
            "source": "Delhi",
            "destination": "Pune",
            "date": "2026-02-22",
            "departure_time": "10:30",
            "arrival_time": "12:00",
            "seats_available": 24,
            "price": 4100,
            "status": "Active",
            "fog_risk": 0.2,
            "rain_risk": 0.3,
            "wind_risk": 0.2,
            "airport_congestion": 0.5,
            "previous_flight_delay": 0.2,
            "delay_probability": 0.3,
            "mobility_friendly": "NO",
        },
    ]
    flights.extend(fixed_flights)
    
    # Define main routes for heavy coverage
    main_routes = [
        ("Delhi", "Mumbai"),
        ("Mumbai", "Delhi"),
        ("Delhi", "Pune"),
        ("Pune", "Delhi"),
        ("Mumbai", "Pune"),
        ("Pune", "Mumbai"),
    ]
    
    # Times for each session
    morning_times = ["06:00", "07:30", "09:00", "10:30"]
    afternoon_times = ["12:00", "13:30", "14:30", "15:30", "16:00", "17:30"]
    evening_times = ["18:00", "19:30", "20:00", "21:00"]
    
    # Dates: Feb 22 and Feb 23, 2026
    dates = ["2026-02-22", "2026-02-23"]
    
    # Generate flights for main routes
    flight_counter = 1000
    for source, destination in main_routes:
        for date in dates:
            for time_slot in [morning_times, afternoon_times, evening_times]:
                for departure_time in time_slot:
                    airline_code, airline_name = random.choice(AIRLINES)
                    flight_id = f"{airline_code}{flight_counter}"
                    flight_counter += 1
                    
                    # Add 1-2 hours travel time
                    arrival_time = add_hours_to_time(departure_time, random.randint(1, 2))
                    
                    flight = {
                        "flight_id": flight_id,
                        "airline": airline_name,
                        "source": source,
                        "destination": destination,
                        "date": date,
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "seats_available": random.randint(5, 95),
                        "price": random.randint(3000, 10000),
                        "status": random.choice(["Active", "Active", "Active", "Active", "Cancelled"]),
                        "fog_risk": round(random.uniform(0, 0.6), 2),
                        "rain_risk": round(random.uniform(0, 0.6), 2),
                        "wind_risk": round(random.uniform(0, 0.4), 2),
                        "airport_congestion": round(random.uniform(0, 0.8), 2),
                        "previous_flight_delay": round(random.uniform(0, 0.3), 2),
                        "delay_probability": round(random.uniform(0, 0.7), 2),
                        "mobility_friendly": random.choice(["YES", "YES", "YES", "NO"]),
                    }
                    flights.append(flight)
    
    # Pad with random flights to other cities
    remaining = count - len(flights)
    base_date = datetime.now() + timedelta(days=1)
    
    for i in range(remaining):
        source = random.choice(INDIAN_CITIES)
        destination = random.choice([c for c in INDIAN_CITIES if c != source])
        date = (base_date + timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
        departure_time = generate_time()
        arrival_time = add_hours_to_time(departure_time, random.randint(1, 3))
        
        airline_code, airline_name = random.choice(AIRLINES)
        flight_id = f"{airline_code}{flight_counter}"
        flight_counter += 1
        
        flight = {
            "flight_id": flight_id,
            "airline": airline_name,
            "source": source,
            "destination": destination,
            "date": date,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "seats_available": random.randint(2, 95),
            "price": random.randint(2000, 12000),
            "status": random.choice(["Active", "Active", "Active", "Cancelled"]),
            "fog_risk": round(random.uniform(0, 1), 2),
            "rain_risk": round(random.uniform(0, 1), 2),
            "wind_risk": round(random.uniform(0, 1), 2),
            "airport_congestion": round(random.uniform(0, 1), 2),
            "previous_flight_delay": round(random.uniform(0, 0.3), 2),
            "delay_probability": round(random.uniform(0, 1), 2),
            "mobility_friendly": random.choice(["YES", "YES", "YES", "NO"]),
        }
        flights.append(flight)
    
    return flights


def seed_flights(flights: List[Dict]):
    """
    Insert flight data into database.
    
    Args:
        flights: List of flight dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executemany("""
    INSERT INTO flights (
        flight_id, airline, source, destination, date, departure_time, arrival_time,
        seats_available, price, status,
        fog_risk, rain_risk, wind_risk,
        airport_congestion, previous_flight_delay, delay_probability, mobility_friendly,
        api_provider, api_flight_key, last_updated_utc, raw_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            f["flight_id"], f["airline"], f["source"], f["destination"], f["date"],
            f["departure_time"], f["arrival_time"],
            f.get("seats_available", 0), f.get("price", 0), f["status"],
            f.get("fog_risk", 0.3), f.get("rain_risk", 0.3), f.get("wind_risk", 0.3),
            f.get("airport_congestion", 0.5), f.get("previous_flight_delay", 0.2), 
            f.get("delay_probability", 0.4),
            f.get("mobility_friendly", "YES"),
            f.get("api_provider"), f.get("api_flight_key"), 
            f.get("last_updated_utc"), f.get("raw_json")
        )
        for f in flights
    ])
    
    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(flights)} flights into database")


def get_flight_by_id(flight_id: str) -> Optional[Dict]:
    """
    Fetch a flight by its ID.
    
    Args:
        flight_id: Flight identifier
        
    Returns:
        Flight dictionary or None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_all_flights() -> List[Dict]:
    """Get all flights from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights")
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def setup_database():
    """Initialize database if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        print("📦 Initializing database...")
        init_db()
        flights = generate_flights(300)
        seed_flights(flights)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(flights)")
    columns = {row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) FROM flights")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM flights WHERE flight_id = ?", ("AI203",))
    has_ai203 = cursor.fetchone()[0] > 0
    cursor.execute("SELECT COUNT(*) FROM flights WHERE flight_id = ?", ("A1203",))
    has_a1203 = cursor.fetchone()[0] > 0
    cursor.execute("SELECT COUNT(*) FROM flights WHERE flight_id = ?", ("SG999",))
    has_sg999 = cursor.fetchone()[0] > 0
    conn.close()

    if "airline" not in columns or "mobility_friendly" not in columns or count < 300 or not has_ai203 or not has_a1203 or not has_sg999:
        print("📦 Rebuilding database with updated schema...")
        init_db()
        flights = generate_flights(300)
        seed_flights(flights)
    else:
        print("✅ Database already exists")


def sync_flights_from_api(source: str, destination: str, date: str) -> tuple[int, str]:
    """
    Sync flights from Aviationstack API into database.
    
    Args:
        source: Source city name (e.g., 'Delhi')
        destination: Destination city name (e.g., 'Mumbai')
        date: Flight date in YYYY-MM-DD format
        
    Returns:
        Tuple of (number_of_flights_synced, status_message)
    """
    try:
        from providers.aviationstack import AviationstackClient, city_to_iata, iata_to_city
        
        # Check if API key is available
        api_key = os.getenv("AVIATIONSTACK_API_KEY")
        if not api_key:
            return (0, "⚠️ API key not found. Set AVIATIONSTACK_API_KEY environment variable or use demo data.")
        
        # Convert city names to IATA codes
        dep_iata = city_to_iata(source)
        arr_iata = city_to_iata(destination)
        
        if not dep_iata or not arr_iata:
            return (0, f"❌ Unknown airport for {source} or {destination}")
        
        # Fetch flights from API
        client = AviationstackClient(api_key)
        normalized_flights = client.fetch_and_normalize(
            dep_iata=dep_iata,
            arr_iata=arr_iata,
            flight_date=date
        )
        
        if not normalized_flights:
            return (0, f"ℹ️ No flights found for {source} → {destination} on {date}")
        
        # Upsert into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        synced_count = 0
        for flight in normalized_flights:
            # Use INSERT OR REPLACE to upsert
            cursor.execute("""
            INSERT OR REPLACE INTO flights (
                flight_id, airline, source, destination, date, departure_time, arrival_time,
                seats_available, price, status,
                fog_risk, rain_risk, wind_risk,
                airport_congestion, previous_flight_delay, delay_probability, mobility_friendly,
                api_provider, api_flight_key, last_updated_utc, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight["flight_id"], flight["airline"], flight["source"], flight["destination"],
                flight["date"], flight["departure_time"], flight["arrival_time"],
                flight.get("seats_available"), flight.get("price"), flight["status"],
                flight.get("fog_risk"), flight.get("rain_risk"), flight.get("wind_risk"),
                flight.get("airport_congestion"), flight.get("previous_flight_delay"),
                flight.get("delay_probability"), flight.get("mobility_friendly", "YES"),
                flight.get("api_provider"), flight.get("api_flight_key"),
                flight.get("last_updated_utc"), flight.get("raw_json")
            ))
            synced_count += 1
        
        conn.commit()
        conn.close()
        
        return (synced_count, f"✅ Synced {synced_count} live flights from Aviationstack API")
        
    except Exception as e:
        return (0, f"❌ API sync failed: {str(e)}")


def has_api_key() -> bool:
    """Check if Aviationstack API key is configured."""
    return bool(os.getenv("AVIATIONSTACK_API_KEY"))



if __name__ == "__main__":
    setup_database()
