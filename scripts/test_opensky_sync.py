"""
Test script for OpenSky Network live data integration.

This script:
1. Syncs live aircraft data from OpenSky Network
2. Verifies data is written to database
3. Displays sample live flights
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from database import sync_live_planes_to_db, setup_database

def main():
    print("=" * 70)
    print("OpenSky Network Live Data Integration Test")
    print("=" * 70)
    print()
    
    # Ensure database is setup
    print("⚙️  Setting up database...")
    setup_database()
    print("✅ Database ready")
    print()
    
    # Sync live data
    print("🛰️  Fetching live aircraft from OpenSky Network...")
    print("   (This may take 5-10 seconds)")
    print()
    
    try:
        stats = sync_live_planes_to_db()
        
        if stats.get("errors") and stats["errors"] > 0:
            print(f"⚠️  Sync completed with errors:")
            print(f"   Error message: {stats.get('error_msg', 'Unknown error')}")
        else:
            print(f"✅ Sync successful!")
            print(f"   Live planes fetched: {stats.get('live_planes', 0)}")
            print(f"   Flights materialized: {stats.get('materialized_flights', 0)}")
        
        print()
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return 1
    
    # Query database for OpenSky flights
    print("-" * 70)
    print("📊 Querying database for OpenSky flights...")
    print()
    
    try:
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        
        # Count OpenSky flights
        cursor.execute("SELECT COUNT(*) FROM flights WHERE data_source='opensky'")
        count = cursor.fetchone()[0]
        print(f"   Total OpenSky flights in database: {count}")
        print()
        
        # Show sample flights
        cursor.execute("""
            SELECT flight_id, airline, source, destination, status, seats_available, price
            FROM flights 
            WHERE data_source='opensky' 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            print("   Sample live flights:")
            print("   " + "-" * 66)
            print(f"   {'Flight ID':<12} {'Airline':<20} {'Route':<25} {'Status':<10}")
            print("   " + "-" * 66)
            for row in results:
                flight_id, airline, source, dest, status, seats, price = row
                route = f"{source} → {dest}"
                print(f"   {flight_id:<12} {airline:<20} {route:<25} {status:<10}")
        else:
            print("   No live flights found in database.")
        
        print()
        
        # Query live_planes table
        cursor.execute("SELECT COUNT(*) FROM live_planes")
        plane_count = cursor.fetchone()[0]
        print(f"   Total aircraft in live_planes table: {plane_count}")
        
        # Show sample aircraft
        cursor.execute("""
            SELECT icao24, callsign, origin_country, lat, lon, altitude_m, velocity_mps, on_ground
            FROM live_planes
            LIMIT 5
        """)
        
        planes = cursor.fetchall()
        if planes:
            print()
            print("   Sample aircraft positions:")
            print("   " + "-" * 66)
            print(f"   {'ICAO24':<8} {'Callsign':<10} {'Country':<15} {'Lat':<8} {'Lon':<8} {'Alt(m)':<8}")
            print("   " + "-" * 66)
            for plane in planes:
                icao24, call, country, lat, lon, alt, vel, grounded = plane
                call = call or "N/A"
                country = country or "Unknown"
                lat_str = f"{lat:.2f}" if lat else "N/A"
                lon_str = f"{lon:.2f}" if lon else "N/A"
                alt_str = f"{int(alt)}" if alt else "N/A"
                print(f"   {icao24:<8} {call:<10} {country:<15} {lat_str:<8} {lon_str:<8} {alt_str:<8}")
        
        conn.close()
        print()
        
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return 1
    
    print("=" * 70)
    print("✅ Test completed successfully!")
    print()
    print("Next steps:")
    print("1. Launch Streamlit: streamlit run app.py")
    print("2. Click 'Sync Live Planes (OpenSky)' in sidebar")
    print("3. Select 'Live Only' in Data Source Filter")
    print("4. Search for flights to see live data")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
