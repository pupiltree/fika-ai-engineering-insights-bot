import sqlite3
import os
import datetime
import random

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect("fika_insights.db")
cur = conn.cursor()

# Create tables if not exist
cur.execute("""
CREATE TABLE IF NOT EXISTS commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    date TEXT,
    additions INTEGER,
    deletions INTEGER,
    files_changed INTEGER
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS pull_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    opened_at TEXT,
    closed_at TEXT,
    merged_at TEXT,
    files_changed INTEGER,
    additions INTEGER,
    deletions INTEGER
);
""")

# Insert fake commits
for _ in range(50):
    author = random.choice(["alice", "bob", "charlie"])
    date = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 14))).isoformat()
    additions = random.randint(10, 500)
    deletions = random.randint(5, 300)
    files_changed = random.randint(1, 15)
    cur.execute("INSERT INTO commits (author, date, additions, deletions, files_changed) VALUES (?, ?, ?, ?, ?)",
                (author, date, additions, deletions, files_changed))

# Insert fake pull requests
for _ in range(20):
    author = random.choice(["alice", "bob", "charlie"])
    days_ago = random.randint(0, 14)
    opened = datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=random.randint(1, 12))
    closed = opened + datetime.timedelta(hours=random.randint(1, 48))
    merged = closed + datetime.timedelta(hours=random.randint(1, 12))
    additions = random.randint(100, 1000)
    deletions = random.randint(50, 700)
    files_changed = random.randint(1, 20)
    cur.execute("""
        INSERT INTO pull_requests (author, opened_at, closed_at, merged_at, files_changed, additions, deletions)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (author, opened.isoformat(), closed.isoformat(), merged.isoformat(), files_changed, additions, deletions))

conn.commit()
conn.close()

print("[✔] Seeded database with fake commits and pull requests.")
