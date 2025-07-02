from langchain_core.tools import tool 

@tool 
def narrate_insights(churn_data):
    """narrate"""
    report="Weekly Summary"
    for record in churn_data:
        report+=f"{record['author']}+{record['additions']}/-{record['deletions']}"
    return report