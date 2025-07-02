import json, random
from datetime import datetime, timedelta

authors = ["jadeja", "deepak", "ayush", "dhoni", "virat"]
messages = [
    "Refactor login API",
    "Fix cart issue",
    "Add test coverage",
    "Optimize queries",
    "Implement CI pipeline",
    "Update docs",
    "Improve test coverage",
    "Bugfix: handle edge case",
    "Feature: add user profile",
    "Chore: update dependencies"
]
commit_types = ["feature", "bugfix", "refactor", "docs", "test", "chore"]

base_time = datetime.now() - timedelta(days=7)
commits = []
prs = []
pr_count = random.randint(10, 18)

# Simulate PRs with review and CI data
for pr_id in range(pr_count):
    pr_author = random.choice(authors)
    pr_created = base_time + timedelta(days=random.randint(0, 6), hours=random.randint(9, 18))
    pr_merged = pr_created + timedelta(hours=random.randint(2, 48))
    pr_review_latency = (pr_merged - pr_created).total_seconds() / 3600
    pr_ci_status = random.choice(["success"]*8 + ["failure"]*2)
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

# Assign commits to PRs and simulate risk/churn
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

mock_data = {
    "repo": "mock-org/mock-repo",
    "fetched_at": datetime.now().isoformat() + "Z",
    "source": "seed_data",
    "commits": commits,
    "prs": prs
}

with open("data/seed_data.json", "w") as f:
    json.dump(mock_data, f, indent=2)
