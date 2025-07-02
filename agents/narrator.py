
def narrate_insights(state):
    churn_data=state["churn_report"]
    """narrate"""
    report="Weekly Summary \n"
    for record in churn_data:
        report+=f"{record['author']}:+{record['additions']}/-{record['deletions']}\n"
    return {**state, "summary":report }