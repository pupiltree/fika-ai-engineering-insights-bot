from typing import Dict
from datetime import datetime, timedelta
import random
import json
import os

def harvest_github_data(state: Dict) -> Dict:
    print("🔍 Using FAKE GitHub data for MVP...")

    authors = ["alice", "bob", "carol", "jai.v"]
    fake_commits = []

    for i in range(10):
        author = random.choice(authors)
        additions = random.randint(10, 150)
        deletions = random.randint(5, 100)
        date = (datetime.now() - timedelta(days=random.randint(0, 6))).isoformat()

        fake_commits.append({
            "sha": f"fake{i}",
            "author": author,
            "additions": additions,
            "deletions": deletions,
            "total": additions + deletions,
            "date": date
        })

    result = {**state, "github_data": {"commits": fake_commits}}

    # ✅ Log input/output
    os.makedirs("logs", exist_ok=True)
    with open("logs/agent_logs.txt", "a") as log:
        log.write("[harvest_github_data] INPUT:\n")
        log.write(json.dumps(state, indent=2) + "\n")
        log.write("[harvest_github_data] OUTPUT:\n")
        log.write(json.dumps(result, indent=2) + "\n\n")

    return result
