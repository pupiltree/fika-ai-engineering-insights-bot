from langchain_core.tools import tool

@tool
def analyze_diff(events):
    """analyze"""
    churn_data = []
    for event in events:
        stats = event.get("stats", {})
        churn_data.append({
            "author": event["commit"]["author"]["name"],
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0)
        })
    return churn_data
