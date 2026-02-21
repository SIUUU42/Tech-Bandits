"""
Database initialization and flight data seeding.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "flights.db"

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
    
    # Create flights table
    cursor.execute("""
    CREATE TABLE flights (
        flight_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        date TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        seats_available INTEGER NOT NULL,
        price INTEGER NOT NULL,
        status TEXT NOT NULL,
        fog_risk REAL NOT NULL,
        rain_risk REAL NOT NULL,
        wind_risk REAL NOT NULL,
        airport_congestion REAL NOT NULL,
        previous_flight_delay REAL NOT NULL,
        delay_probability REAL NOT NULL
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
    airlines = ["AI", "SG", "BA", "6E", "UK", "I5", "G8"]  # Air India, SpiceJet, British, IndiGo, Vistara, etc.
    airline = random.choice(airlines)
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


def generate_flights(count: int = 150) -> List[Dict]:
    """
    Generate realistic Indian domestic flight data.
    
    Args:
        count: Number of flights to generate (default 150)
        
    Returns:
        List of flight dictionaries
    """
    flights = []
    base_date = datetime.now() + timedelta(days=1)
    
    for i in range(count):
        source = random.choice(INDIAN_CITIES)
        destination = random.choice([c for c in INDIAN_CITIES if c != source])
        date = (base_date + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
        departure_time = generate_time()
        arrival_time = add_hours_to_time(departure_time, random.randint(1, 3))
        
        flight = {
            "flight_id": generate_flight_id(),
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
        flight_id, source, destination, date, departure_time, arrival_time,
        seats_available, price, status,
        fog_risk, rain_risk, wind_risk,
        airport_congestion, previous_flight_delay, delay_probability
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            f["flight_id"], f["source"], f["destination"], f["date"],
            f["departure_time"], f["arrival_time"],
            f["seats_available"], f["price"], f["status"],
            f["fog_risk"], f["rain_risk"], f["wind_risk"],
            f["airport_congestion"], f["previous_flight_delay"], f["delay_probability"]
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
        flights = generate_flights(150)
        seed_flights(flights)
    else:
        print("✅ Database already exists")


if __name__ == "__main__":
    setup_database()
