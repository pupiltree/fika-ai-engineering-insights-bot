import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.db import init_db, insert_commits, insert_prs

# This script is now deprecated. Use storage.db.load_seed_data() from Python shell or integrate in your Makefile or main pipeline.
print("[DEPRECATED] Use storage.db.load_seed_data() instead.")

def main():
    seed_path = os.path.join('data', 'seed_data.json')
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

if __name__ == "__main__":
    main()
