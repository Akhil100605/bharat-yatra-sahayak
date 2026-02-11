import sqlite3

conn = sqlite3.connect("bharat_yatra.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM tourist_places WHERE place='Golconda'")

conn.commit()
conn.close()

print("Duplicate entry removed.")
