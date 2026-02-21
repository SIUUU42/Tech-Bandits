"""
Database initialization and flight data seeding.
"""

import sqlite3
import os
import random
import json
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
    
    # Create flights table
    cursor.execute("""
    CREATE TABLE flights (
        flight_id TEXT PRIMARY KEY,
        airline TEXT NOT NULL,
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
        delay_probability REAL NOT NULL,
        mobility_friendly TEXT NOT NULL DEFAULT 'YES'
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
        airport_congestion, previous_flight_delay, delay_probability, mobility_friendly
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            f["flight_id"], f["airline"], f["source"], f["destination"], f["date"],
            f["departure_time"], f["arrival_time"],
            f["seats_available"], f["price"], f["status"],
            f["fog_risk"], f["rain_risk"], f["wind_risk"],
            f["airport_congestion"], f["previous_flight_delay"], f["delay_probability"],
            f["mobility_friendly"]
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
        migrate_schema()  # Add live data support
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
    
    # Always run migration to ensure live data tables exist
    migrate_schema()
    print("✅ Database ready")


def migrate_schema():
    """
    Migration-safe schema updates for live data support.
    Adds live_planes table and new columns to flights without dropping data.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create live_planes table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_planes (
            icao24 TEXT PRIMARY KEY,
            callsign TEXT,
            origin_country TEXT,
            last_contact_utc TEXT,
            lat REAL,
            lon REAL,
            altitude_m REAL,
            velocity_mps REAL,
            heading_deg REAL,
            on_ground INTEGER,
            raw_json TEXT,
            updated_at_utc TEXT
        )
        """)
        
        # Add new columns to flights table if they don't exist
        cursor.execute("PRAGMA table_info(flights)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # SQLite doesn't support adding NOT NULL columns to existing tables easily
        # So we add them as nullable and handle defaults in code
        if "data_source" not in existing_columns:
            cursor.execute("ALTER TABLE flights ADD COLUMN data_source TEXT DEFAULT 'fake'")
            print("  ➕ Added data_source column")
        
        if "raw_json" not in existing_columns:
            cursor.execute("ALTER TABLE flights ADD COLUMN raw_json TEXT")
            print("  ➕ Added raw_json column")
        
        if "last_updated_utc" not in existing_columns:
            cursor.execute("ALTER TABLE flights ADD COLUMN last_updated_utc TEXT")
            print("  ➕ Added last_updated_utc column")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"⚠️  Migration warning: {e}")
    finally:
        conn.close()


def sync_live_planes_to_db() -> Dict[str, int]:
    """
    Fetch live aircraft data from OpenSky and materialize into flights table.
    
    Returns:
        Dict with counts: {"live_planes": N, "materialized_flights": M, "errors": E}
    """
    try:
        from providers.opensky import (
            fetch_india_flights, 
            infer_airline_from_callsign,
            infer_nearest_city
        )
    except ImportError:
        return {"live_planes": 0, "materialized_flights": 0, "errors": 1, 
                "error_msg": "OpenSky provider not available"}
    
    stats = {"live_planes": 0, "materialized_flights": 0, "errors": 0}
    
    try:
        # Fetch live data from OpenSky
        print("🛰️  Fetching live flight data from OpenSky...")
        planes = fetch_india_flights(timeout=15)
        stats["live_planes"] = len(planes)
        print(f"   Found {len(planes)} aircraft")
        
        if not planes:
            return stats
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Upsert into live_planes table
        for plane in planes:
            cursor.execute("""
            INSERT OR REPLACE INTO live_planes (
                icao24, callsign, origin_country, last_contact_utc,
                lat, lon, altitude_m, velocity_mps, heading_deg, on_ground,
                raw_json, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plane["icao24"],
                plane["callsign"],
                plane["origin_country"],
                datetime.utcfromtimestamp(plane["last_contact"]).isoformat() if plane["last_contact"] else None,
                plane["latitude"],
                plane["longitude"],
                plane["baro_altitude"],
                plane["velocity"],
                plane["true_track"],
                1 if plane["on_ground"] else 0,
                json.dumps(plane),
                datetime.utcnow().isoformat()
            ))
        
        # Materialize live_planes into flights table for UI compatibility
        print("🔄 Materializing live planes into flights...")
        now_utc = datetime.utcnow()
        current_date = now_utc.strftime("%Y-%m-%d")
        current_time = now_utc.strftime("%H:%M")
        
        for plane in planes:
            # Generate pseudo flight record
            callsign = plane["callsign"] or ""
            flight_id = callsign.strip() if callsign.strip() else plane["icao24"]
            airline = infer_airline_from_callsign(callsign) if callsign else plane["origin_country"]
            
            # Infer location
            source, destination = infer_nearest_city(plane["latitude"], plane["longitude"])
            
            # Arrival time = departure + 2 hours (placeholder)
            arrival_time = (now_utc +timedelta(hours=2)).strftime("%H:%M")
            
            # Status based on ground state
            status = "On Ground" if plane.get("on_ground") else "Active"
            
            # Default risk values for live data
            fog_risk = 0.2
            rain_risk = 0.2
            wind_risk = 0.2
            airport_congestion = 0.3
            previous_flight_delay = 0.2
            delay_probability = 0.3
            
            # Insert or replace flight
            cursor.execute("""
            INSERT OR REPLACE INTO flights (
                flight_id, airline, source, destination, date, departure_time, arrival_time,
                seats_available, price, status,
                fog_risk, rain_risk, wind_risk,
                airport_congestion, previous_flight_delay, delay_probability,
                mobility_friendly, data_source, raw_json, last_updated_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight_id, airline, source, destination, current_date, current_time, arrival_time,
                0,  # seats_available unknown
                0,  # price unknown
                status,
                fog_risk, rain_risk, wind_risk,
                airport_congestion, previous_flight_delay, delay_probability,
                "YES",  # Assume mobility friendly
                "opensky",
                json.dumps(plane),
                now_utc.isoformat()
            ))
            stats["materialized_flights"] += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Synced {stats['live_planes']} live planes → {stats['materialized_flights']} flights")
        return stats
        
    except Exception as e:
        stats["errors"] = 1
        stats["error_msg"] = str(e)
        print(f"❌ Error syncing live data: {e}")
        return stats


if __name__ == "__main__":
    setup_database()
