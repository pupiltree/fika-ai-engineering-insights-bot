# import sqlite3

# def init_db():
#     conn = sqlite3.connect('fika.db')
#     c = conn.cursor()
#     c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, data TEXT)")
#     conn.commit()
#     conn.close()

import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS events 
                 (id TEXT PRIMARY KEY, type TEXT, actor TEXT, 
                  created_at TEXT, repo TEXT, data TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS metrics 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, metric_type TEXT, value REAL)''')
    
    conn.commit()
    conn.close()

def save_event(event):
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO events 
                 (id, type, actor, created_at, repo, data) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (event['id'], event['type'], event['actor'], 
               event['created_at'], event['repo'], json.dumps(event)))
    
    conn.commit()
    conn.close()

def get_recent_events(limit=50):
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM events ORDER BY created_at DESC LIMIT ?', (limit,))
    events = c.fetchall()
    
    conn.close()
    return events
