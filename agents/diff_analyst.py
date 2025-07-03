def analyze_churn(data):
    churn_results = []
    commits = data.get("commits", [])

    for commit in commits:
        author = commit.get("author", "Unknown")
        additions = commit.get("stats", {}).get("additions", 0)
        deletions = commit.get("stats", {}).get("deletions", 0)
        churn = additions + deletions

        churn_results.append({
            "author": author,
            "churn": churn,
            "message": commit.get("message", ""),
            "sha": commit.get("sha", "")
        })

    return churn_results
