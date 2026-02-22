import sqlite3

conn = sqlite3.connect('flights.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT data_source FROM flights')
sources = cursor.fetchall()
print('Data sources in database:')
for source in sources:
    cursor.execute('SELECT COUNT(*) FROM flights WHERE data_source = ?', source)
    count = cursor.fetchone()[0]
    print(f"  {source[0] or 'NULL'}: {count} flights")

conn.close()
