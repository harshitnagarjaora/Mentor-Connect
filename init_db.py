import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Matches table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mentor_id INTEGER,
        mentee_id INTEGER,
        scheduled_time TEXT,
        FOREIGN KEY (mentor_id) REFERENCES users(id),
        FOREIGN KEY (mentee_id) REFERENCES users(id)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        timestamp TEXT
    )
''')
#cursor.execute('ALTER TABLE users ADD COLUMN peer_id TEXT')
#cursor.execute('ALTER TABLE matches ADD COLUMN status TEXT')
cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN expertise TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN education TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN skills TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN experience TEXT")


conn.commit()
conn.close()

print("Database initialized successfully.")