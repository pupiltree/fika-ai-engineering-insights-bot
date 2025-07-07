import json
import os
from datetime import datetime, timedelta

fake_commits = []
for i in range(5):
    fake_commits.append({
        "commit": {
            "author": {
                "name": f"Dev{i}",
                "date": (datetime.now() - timedelta(days=i)).isoformat()
            }
        },
        "sha": f"dummysha{i}"
    })

os.makedirs("seedData", exist_ok=True)
with open("seedData/fake_commits.json", "w") as f:
    json.dump(fake_commits, f, indent=2)