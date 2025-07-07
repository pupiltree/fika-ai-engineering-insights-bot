def diff_analyst_node(state):
    commits = state["commits"]
    churn = len(commits) * 10 
    return {"churn": churn, "commits": commits}