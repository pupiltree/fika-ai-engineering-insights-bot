
def analyze_diff(state):
    """analyze"""
    events=state["commits"]
    churn_data = []
    for event in events:
        stats = event.get("stats", {})
        churn_data.append({
            "author": event["commit"]["author"]["name"],
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0)
        })
    return {**state, "churn_report": churn_data}

def analyze_prs(state):
    """analyze pull requests"""
    events=state["pull_requests"]
    pr_data = []
    for event in events:
        stats = event.get("stats", {})
        pr_data.append({
            "user": event["user"]["login"],
            "title":event["title"],
            "body":event["body"]
        })
    return {**state, "pr_insights": pr_data}
