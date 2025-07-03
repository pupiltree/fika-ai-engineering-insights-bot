from data_analyst_agent.analytics import data_analytics
from langchain_core.tools import tool

@tool
def diff_analyst_agent(commits: list, pull_requests: list) -> dict:
    """
    Analyze commits and pull requests to extract developer metrics and code churn.
    """
    return data_analytics(commits, pull_requests)