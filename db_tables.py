import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Replace 'users' with 'matches' to see match table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("Entries in users table:")
for row in rows:
    print(row)

conn.close()
