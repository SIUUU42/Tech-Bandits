import sqlite3

conn = sqlite3.connect('flights.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== Checking database ===')

# Check flights with Delhi source
print('\n1. Delhi to Mumbai flights:')
cursor.execute("SELECT flight_id, source, destination, date, departure_time, status FROM flights WHERE source='Delhi' AND destination='Mumbai' LIMIT 5")
results = cursor.fetchall()
print(f'Found: {len(results)}')
for row in results:
    print(f"  {row['flight_id']} - {row['source']} → {row['destination']} on {row['date']} at {row['departure_time']} ({row['status']})")

# Check total count
cursor.execute('SELECT COUNT(*) FROM flights')
print(f'\n2. Total flights in DB: {cursor.fetchone()[0]}')

# Check dates available
cursor.execute('SELECT DISTINCT date FROM flights ORDER BY date')
dates = [row[0] for row in cursor.fetchall()]
print(f'\n3. Available dates: {dates}')

# Check destinations
cursor.execute('SELECT DISTINCT destination FROM flights LIMIT 10')
dests = [row[0] for row in cursor.fetchall()]
print(f'\n4. Sample destinations: {dests}')

# Check Delhi flights
cursor.execute('SELECT COUNT(*) FROM flights WHERE source="Delhi"')
print(f'\n5. Total Delhi source flights: {cursor.fetchone()[0]}')

# Check Mumbai destinations
cursor.execute('SELECT COUNT(*) FROM flights WHERE destination="Mumbai"')
print(f'\n6. Total Mumbai destination flights: {cursor.fetchone()[0]}')

conn.close()
