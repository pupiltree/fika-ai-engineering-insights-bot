import json, random
from datetime import datetime, timedelta


# ------------------- Simulate Authors & Commits -------------------
authors = ["jadeja", "deepak", "ayush", "dhoni", "virat"]
messages = [
    "Refactor login API", "Fix cart issue", "Add test coverage",
    "Optimize queries", "Implement CI pipeline", "Update docs",
    "Improve test coverage", "Bugfix: handle edge case",
    "Feature: add user profile", "Chore: update dependencies"
]
commit_types = ["feature", "bugfix", "refactor", "docs", "test", "chore"]

# ------------------- Time Simulation -------------------
base_time = datetime.now() - timedelta(days=7)
commits = []
prs = []
pr_count = random.randint(10, 18)


# ------------------- Create PRs -------------------
for pr_id in range(pr_count):
    pr_author = random.choice(authors)
    pr_created = base_time + timedelta(days=random.randint(0, 6), hours=random.randint(9, 18))
    pr_merged = pr_created + timedelta(hours=random.randint(2, 48))
    pr_review_latency = (pr_merged - pr_created).total_seconds() / 3600
    pr_ci_status = random.choice(["success"] * 8 + ["failure"] * 2)  # 80% success rate
    pr_commits = random.randint(2, 5)

    prs.append({
        "pr_id": f"PR{pr_id:03}",
        "author": pr_author,
        "created_at": pr_created.isoformat() + "Z",
        "merged_at": pr_merged.isoformat() + "Z",
        "review_latency_hrs": round(pr_review_latency, 2),
        "ci_status": pr_ci_status,
        "commits": []
    })


# ------------------- Create Commits -------------------
for i in range(50):
    pr = random.choice(prs)
    dt = base_time + timedelta(days=random.randint(0, 6), hours=random.randint(7, 22))
    add = random.randint(30, 400)
    delete = random.randint(10, 250)
    churn = add + delete
    is_risky = churn > 350 or random.random() < 0.1
    after_hours = dt.hour < 9 or dt.hour > 19
    commit_type = random.choice(commit_types)
    author = random.choice(authors)

    commit = {
        "sha": f"mocksha{i:04}",
        "author": author,
        "date": dt.isoformat() + "Z",
        "message": random.choice(messages),
        "additions": add,
        "deletions": delete,
        "files_changed": random.randint(1, 6),
        "pr_id": pr["pr_id"],
        "type": commit_type,
        "is_risky": is_risky,
        "after_hours": after_hours
    }

    commits.append(commit)
    pr["commits"].append(commit["sha"])


# ------------------- Calculate DORA Metrics -------------------
def calculate_dora_metrics(pr_list):
    if not pr_list:
        return {
            "lead_time": 0,
            "deploy_frequency": 0,
            "change_failure_rate": 0,
            "mttr": 0
        }

    # Lead Time (in hours): avg time between PR created and merged
    lead_times = [(datetime.fromisoformat(pr["merged_at"][:-1]) - datetime.fromisoformat(pr["created_at"][:-1])).total_seconds() / 3600 for pr in pr_list]
    avg_lead_time = round(sum(lead_times) / len(lead_times), 2)

    # Deployment Frequency: count of PRs merged per week
    merged_dates = [datetime.fromisoformat(pr["merged_at"][:-1]) for pr in pr_list]
    days_range = (max(merged_dates) - min(merged_dates)).days or 1
    deploy_frequency = round(len(pr_list) / (days_range / 7), 2)

    # Change Failure Rate: % of PRs where ci_status == failure
    failures = sum(1 for pr in pr_list if pr.get("ci_status") == "failure")
    change_failure_rate = round((failures / len(pr_list)) * 100, 2)

    # MTTR (Mean Time To Recovery): Simulated as a random value between 1-3 hours
    mttr = round(random.uniform(1.0, 3.0), 2)

    return {
        "lead_time": avg_lead_time,
        "deploy_frequency": deploy_frequency,
        "change_failure_rate": change_failure_rate,
        "mttr": mttr
    }


# ------------------- Assemble Final JSON -------------------
mock_data = {
    "repo": "mock-org/mock-repo",
    "fetched_at": datetime.now().isoformat() + "Z",
    "source": "seed_data",
    "commits": commits,
    "prs": prs,
    "dora_metrics": calculate_dora_metrics(prs)
}


# ------------------- Save JSON -------------------
import os
os.makedirs("data", exist_ok=True)

with open("data/seed_data.json", "w") as f:
    json.dump(mock_data, f, indent=2)

print("✅ Seed data with DORA metrics generated successfully → data/seed_data.json")
