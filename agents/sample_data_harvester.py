import json
import os
from collections import defaultdict

def sample_data_harvester(state):
    print("\n📁 [SampleDataAgent] Loading sample commit data from /data/sample_commits.json")

    try:
        with open(os.path.join("data", "commits.json"), "r") as f:
            commits = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load sample commits: {e}")
        commits = []

    print(f"✅ Loaded {len(commits)} sample commits.")

    state["commits"] = commits

    
    file_changes = defaultdict(int)
    for commit in commits:
        for file in commit.get("files_changed", []):
            file_changes[file["filename"]] += 1

    state["file_hotspots"] = dict(sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10])
    return state
