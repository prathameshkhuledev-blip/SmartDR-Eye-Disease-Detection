import sqlite3

conn = sqlite3.connect('eye_disease.db')
cur = conn.cursor()

# Check tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables found:', tables)

# Check patient count
try:
    cur.execute('SELECT COUNT(*) FROM patients')
    print('Patient count:', cur.fetchone()[0])

    cur.execute('SELECT * FROM patients')
    rows = cur.fetchall()
    print('Patient rows:', rows)
except Exception as e:
    print('Error reading patients:', e)

# Check prediction count
try:
    cur.execute('SELECT COUNT(*) FROM predictions')
    print('Prediction count:', cur.fetchone()[0])
except Exception as e:
    print('Error reading predictions:', e)

conn.close()