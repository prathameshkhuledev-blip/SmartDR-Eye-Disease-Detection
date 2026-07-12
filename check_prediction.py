import sqlite3

conn = sqlite3.connect('eye_disease.db')
cur = conn.cursor()

# Get all column names from predictions table
cur.execute("PRAGMA table_info(predictions)")
columns = [col[1] for col in cur.fetchall()]
print("Prediction columns:", columns)
print()

# Get all prediction rows
cur.execute("SELECT * FROM predictions")
rows = cur.fetchall()

if not rows:
    print("No predictions found.")
else:
    for row in rows:
        print("-------------------------------")
        for col, val in zip(columns, row):
            print(f"  {col}: {val}")
        print()

conn.close()