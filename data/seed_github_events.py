import sys
import os

# Ensure the parent directory is in sys.path for local imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"sys.path: {sys.path}")

"""
Script to seed the database with fake GitHub events for demo and testing purposes.
"""

import random
from datetime import datetime, timedelta
from fika_db import database

authors = ["alice", "bob", "carol", "dave"]
messages = [
    "Initial commit",
    "Fix bug in user login",
    "Add new feature: dashboard",
    "Refactor codebase",
    "Improve test coverage",
    "Update dependencies",
    "Optimize query performance"
]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def seed_commits(n=20):
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    for i in range(n):
        commit = {
            "id": f"commit_{i}",
            "author": random.choice(authors),
            "message": random.choice(messages),
            "additions": random.randint(1, 100),
            "deletions": random.randint(0, 50),
            "changed_files": random.randint(1, 5),
            "timestamp": random_date(week_ago, now).isoformat()
        }
        database.insert_commit(commit)
    print(f"Seeded {n} commits.")

def seed_pull_requests(n=5):
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    for i in range(n):
        created_at = random_date(week_ago, now)
        merged_at = created_at + timedelta(hours=random.randint(1, 48))
        pr = {
            "id": f"pr_{i}",
            "author": random.choice(authors),
            "title": f"PR Title {i}",
            "additions": random.randint(10, 200),
            "deletions": random.randint(0, 100),
            "changed_files": random.randint(1, 10),
            "created_at": created_at.isoformat(),
            "merged_at": merged_at.isoformat(),
            "review_latency": random.randint(1, 24),
            "ci_status": random.choice(["success", "failure"])
        }
        database.insert_pull_request(pr)
    print(f"Seeded {n} pull requests.")

def main():
    print("Initializing database...")
    database.init_db()
    print("Database initialized.")
    seed_commits()
    seed_pull_requests()
    print("Seeded database with fake GitHub events.")
    print("If you see 'fika_ai_insights.db' in your project root, seeding was successful.")

if __name__ == "__main__":
    main() 