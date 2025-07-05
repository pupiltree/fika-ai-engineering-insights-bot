# storage.py
import sqlite3

DB_PATH = 'botdata.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        author TEXT,
        additions INTEGER,
        deletions INTEGER,
        files INTEGER,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def save_event(event):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO events (type, author, additions, deletions, files, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (event['type'], event['author'], event['additions'], event['deletions'], event['files'], event['timestamp']))
    conn.commit()
    conn.close()

def get_commits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM events WHERE type = "commit"')
    rows = c.fetchall()
    conn.close()
    return rows

def save_analytics(analytics):
    # TODO: Save analytics results
    pass 