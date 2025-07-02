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
from fika_db.database import init_database, insert_commit, insert_pull_request

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
        commit_hash = f"commit_{i}"
        author = random.choice(authors)
        message = random.choice(messages)
        additions = random.randint(1, 100)
        deletions = random.randint(0, 50)
        changed_files = random.randint(1, 5)
        timestamp = random_date(week_ago, now).isoformat()
        
        insert_commit(commit_hash, author, message, timestamp, additions, deletions, changed_files)
    print(f"Seeded {n} commits.")

def seed_pull_requests(n=5):
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    for i in range(n):
        created_at = random_date(week_ago, now)
        merged_at = created_at + timedelta(hours=random.randint(1, 48))
        
        pr_number = i + 1
        title = f"PR Title {i}"
        author = random.choice(authors)
        additions = random.randint(10, 200)
        deletions = random.randint(0, 100)
        changed_files = random.randint(1, 10)
        created_at_str = created_at.isoformat()
        merged_at_str = merged_at.isoformat()
        status = "merged"
        
        insert_pull_request(pr_number, title, author, created_at_str, merged_at_str, additions, deletions, changed_files, status)
    print(f"Seeded {n} pull requests.")

def main():
    print("Initializing database...")
    init_database()
    print("Database initialized.")
    seed_commits()
    seed_pull_requests()
    print("Seeded database with fake GitHub events.")
    print("If you see 'fika_ai_insights.db' in your project root, seeding was successful.")

if __name__ == "__main__":
    main() 