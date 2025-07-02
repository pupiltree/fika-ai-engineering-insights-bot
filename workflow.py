from langgraph.graph import StateGraph

from agents.data_harvester import fetch_github_events
from agents.diff_analyst import analyze_diff
from agents.narrator import narrate_insights
from typing import TypedDict, List, Dict

class DevState(TypedDict):
    token:str
    repo:str
    pull_requests:List[Dict]
    commits: List[Dict]
    churn_report: List[Dict]
    summary: str


def build_flow():
    graph=StateGraph(DevState)
    graph.add_node("Fetch commits",fetch_github_events)
    graph.add_node("Analyze the data",analyze_diff)
    graph.add_node("Narrate",narrate_insights)
    
    graph.set_entry_point("Fetch commits")
    graph.add_edge("Fetch commits","Analyze the data")
    graph.add_edge("Analyze the data","Narrate")
    graph.set_finish_point("Narrate")

    final=graph.compile()
    
    result=final.invoke({
        "repo":"vnshrwt27/fika-ai-engineering-insights-bot",
        "token":" "})
    print(result.get("summary"))
build_flow()