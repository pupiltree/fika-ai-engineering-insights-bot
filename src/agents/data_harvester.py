import json
import os
from dotenv import load_dotenv

load_dotenv()

def data_harvester_node(state):
    with open("src/seed/seedData/fake_commits.json") as f:
        commits = json.load(f)
    parsed = []
    for c in commits:
        parsed.append({
            "author": c["commit"]["author"]["name"],
            "date": c["commit"]["author"]["date"],
            "sha": c["sha"]
        })
    return {"commits": parsed}