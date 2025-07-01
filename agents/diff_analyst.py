# diff_analyst.py
from collections import defaultdict

def diff_analyst_node(state):
    print("\n📊 [DiffAnalystAgent] Analyzing commit data...")
    
    data = state.get("commit_data", [])
    churn_by_user = defaultdict(lambda: {"commits": 0, "lines_added": 0, "lines_deleted": 0})

    for entry in data:
        user = entry["author"]
        churn_by_user[user]["commits"] += 1
        churn_by_user[user]["lines_added"] += entry["additions"]
        churn_by_user[user]["lines_deleted"] += entry["deletions"]

    for user, stats in churn_by_user.items():
        print(f"→ {user}: {stats}")

    print("✅ Analysis complete.")
    state["analysis"] = churn_by_user
    return state
