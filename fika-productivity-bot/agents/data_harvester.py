
import json
from typing import List, Dict
from pathlib import Path

SEED_FILE = Path("data/seed_github.json")


def load_seed_events() -> List[Dict]:
    """Load seed GitHub events from local file"""
    with open(SEED_FILE, "r") as f:
        return json.load(f)


def extract_commit_data(events: List[Dict]) -> List[Dict]:
    """Extract normalized commit-level data from events"""
    commits = []
    for event in events:
        if event["type"] == "PushEvent":
            commit = event["commit"]
            commits.append({
                "author": event["actor"],
                "repo": event["repo"],
                "timestamp": commit["timestamp"],
                "message": commit["message"],
                "additions": commit["additions"],
                "deletions": commit["deletions"],
                "files_changed": commit["files_changed"],
            })
    return commits


def extract_pr_data(events: List[Dict]) -> List[Dict]:
    """Extract normalized PR-level data from events"""
    prs = []
    for event in events:
        if event["type"] == "PullRequestEvent":
            pr = event["pr"]
            prs.append({
                "author": event["actor"],
                "repo": event["repo"],
                "number": pr["number"],
                "additions": pr["additions"],
                "deletions": pr["deletions"],
                "files_changed": pr["files_changed"],
                "created_at": pr["created_at"],
                "merged_at": pr["merged_at"],
                "merged": pr["merged"]
            })
    return prs


def harvest_data() -> Dict[str, List[Dict]]:
    """Return parsed commits and PRs"""
    events = load_seed_events()
    return {
        "commits": extract_commit_data(events),
        "prs": extract_pr_data(events)
    }


if __name__ == "__main__":
    data = harvest_data()
    print("Commits:", data["commits"])
    print("PRs:", data["prs"])
