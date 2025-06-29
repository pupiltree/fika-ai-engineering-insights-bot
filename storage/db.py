import sqlite3

def init_db():
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, data TEXT)")
    conn.commit()
    conn.close()
