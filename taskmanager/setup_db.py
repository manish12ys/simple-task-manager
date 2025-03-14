import sqlite3

# Connect to the database (creates a new one if not existing)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create `users` table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create `tasks` table
c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        date_to_complete TEXT NOT NULL,
        priority TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
''')

conn.commit()
conn.close()

print("Database created successfully!")
