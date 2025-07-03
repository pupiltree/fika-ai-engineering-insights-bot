
def narrate_insights(state):
    """narrate"""

    churn_data=state["churn_report"]
    pr_insight=state["pr_insights"]
    print(pr_insight)
    report="Weekly Summary \n"
    for record in churn_data:
        report+=f"{record['author']}:+{record['additions']}/-{record['deletions']}\n"
    return {**state, "summary":report ,"pr_insights":pr_insight}