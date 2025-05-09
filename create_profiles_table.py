import sqlite3

conn = sqlite3.connect('database.db')  # Make sure this is your actual DB file
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        photo TEXT,
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        expertise TEXT,
        education TEXT,
        experience TEXT,
        bio TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')


conn.commit()
conn.close()

print("✅ profiles table created.")
