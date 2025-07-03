import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = os.getenv("INSIGHTS_DB_PATH", "storage/db.db")


os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS commits (
                sha TEXT PRIMARY KEY,
                author TEXT,
                date TEXT,
                message TEXT,
                additions INTEGER,
                deletions INTEGER,
                files_changed INTEGER,
                pr_id TEXT,
                type TEXT,
                is_risky INTEGER,
                after_hours INTEGER
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS prs (
                pr_id TEXT PRIMARY KEY,
                author TEXT,
                created_at TEXT,
                merged_at TEXT,
                review_latency_hrs REAL,
                ci_status TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_at TEXT,
                report TEXT
            )''')
            conn.commit()
    except Exception as e:
        print(f"DB error initializing: {e}")

def insert_commits(commits: List[Dict[str, Any]]):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.executemany('''INSERT OR REPLACE INTO commits VALUES (?,?,?,?,?,?,?,?,?,?,?)''', [
                (
                    commit.get('sha'),
                    commit.get('author'),
                    commit.get('date'),
                    commit.get('message'),
                    commit.get('additions', 0),
                    commit.get('deletions', 0),
                    commit.get('files_changed', 0),
                    commit.get('pr_id'),
                    commit.get('type'),
                    int(commit.get('is_risky', False)),
                    int(commit.get('after_hours', False))
                ) for commit in commits
            ])
    except Exception as e:
        print(f"DB error inserting commits: {e}")

def insert_prs(prs: List[Dict[str, Any]]):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.executemany('''INSERT OR REPLACE INTO prs VALUES (?,?,?,?,?,?)''', [
                (
                    pr.get('pr_id'),
                    pr.get('author'),
                    pr.get('created_at'),
                    pr.get('merged_at'),
                    pr.get('review_latency_hrs'),
                    pr.get('ci_status')
                ) for pr in prs
            ])
    except Exception as e:
        print(f"DB error inserting PRs: {e}")

def insert_report(report: str, generated_at: str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO reports (generated_at, report) VALUES (?,?)''', (generated_at, report))
    except Exception as e:
        print(f"DB error inserting report: {e}")

def get_latest_report() -> str:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''SELECT report FROM reports ORDER BY generated_at DESC LIMIT 1''')
            row = c.fetchone()
            return row[0] if row else "No report found."
    except Exception as e:
        print(f"DB error fetching latest report: {e}")
        return "No report found."

def load_seed_data(seed_path: str = 'data/seed_data.json'):
    import json
    if not os.path.exists(seed_path):
        print(f"Seed file not found: {seed_path}")
        return
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    commits = data.get('commits', [])
    prs = data.get('prs', [])
    print(f"Seeding {len(commits)} commits and {len(prs)} PRs into the database...")
    init_db()
    insert_commits(commits)
    insert_prs(prs)
    print("Seed data loaded into the database.")
