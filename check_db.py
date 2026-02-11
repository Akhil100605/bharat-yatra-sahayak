import sqlite3

conn = sqlite3.connect("bharat_yatra.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM tourist_places")
print(cursor.fetchone())

conn.close()
