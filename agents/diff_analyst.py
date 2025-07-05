from typing import Dict
from collections import defaultdict
from datetime import datetime
import json
import os
import statistics

def analyze_commit_churn(state: Dict) -> Dict:
    commits = state.get("github_data", {}).get("commits", [])
    author_stats = defaultdict(lambda: {"additions": 0, "deletions": 0, "commits": 0})
    high_churn_commits = []
    risky_commits = []
    daily_churn = defaultdict(int)

    for c in commits:
        author = c["author"]
        additions = c["additions"]
        deletions = c["deletions"]
        churn = additions + deletions

        # Stats per author
        author_stats[author]["additions"] += additions
        author_stats[author]["deletions"] += deletions
        author_stats[author]["commits"] += 1

        # Daily churn aggregation
        date_str = c["date"][:10]  # YYYY-MM-DD
        daily_churn[date_str] += churn

        # Flag high churn commits
        if churn > 200:
            c["churn"] = churn
            high_churn_commits.append(c)
            risky_commits.append({
                "author": author,
                "sha": c["sha"],
                "date": c["date"],
                "churn": churn
            })

    # Spike detection
    churn_values = list(daily_churn.values())
    spike_days = []
    if len(churn_values) >= 2:
        mean = statistics.mean(churn_values)
        stdev = statistics.stdev(churn_values)
        threshold = mean + 1.5 * stdev
        spike_days = [date for date, churn in daily_churn.items() if churn > threshold]

    result = {
        **state,
        "metrics": {
            "author_stats": dict(author_stats),
            "high_churn_commits": high_churn_commits,
            "risky_commits": risky_commits,
            "daily_churn": dict(daily_churn),
            "spike_days": spike_days
        }
    }

    # ✅ Log input/output
    os.makedirs("logs", exist_ok=True)
    with open("logs/agent_logs.txt", "a") as log:
        log.write("[analyze_commit_churn] INPUT:\n")
        log.write(json.dumps(state, indent=2) + "\n")
        log.write("[analyze_commit_churn] OUTPUT:\n")
        log.write(json.dumps(result, indent=2) + "\n\n")

    return result
