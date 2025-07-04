from langgraph.graph import StateGraph

from agents.data_harvester import fetch_github_events,fetch_prs
from agents.diff_analyst import analyze_diff,analyze_prs
from agents.narrator import narrate_insights
from typing import TypedDict, List, Dict


class DevState(TypedDict):
    token:str
    repo:str
    pull_requests:List[Dict]
    commits: List[Dict]
    churn_report: List[Dict]
    summary: str
    pr_insights:str


def build_flow(return_result=False):
    graph=StateGraph(DevState)
    graph.add_node("Fetch commits",fetch_github_events)
    graph.add_node("Fetch Pull Requests",fetch_prs)
    graph.add_node("Analyze the data",analyze_diff)
    graph.add_node("Analyze Pull Requests",analyze_prs)
    graph.add_node("Narrate",narrate_insights)
    
    graph.set_entry_point("Fetch commits")
    
    graph.add_edge("Fetch commits","Fetch Pull Requests")
    graph.add_edge("Fetch Pull Requests","Analyze the data")
    graph.add_edge("Analyze the data","Analyze Pull Requests")
    graph.add_edge("Analyze Pull Requests","Narrate")
    graph.set_finish_point("Narrate")

    final=graph.compile()
    
    result=final.invoke({
        "repo":"pupiltree/fika-ai-engineering-insights-bot",
        "token":" "})
    if return_result:
        return result