from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from typing import Dict, Any

from agents.data_harvester import harvest_github_data
from agents.diff_analyst import analyze_commit_churn
from agents.insight_narrator import generate_insight_summary

# Simple schema as dict[str, Any]
state_schema = Dict[str, Any]

def build_graph():
    workflow = StateGraph(state_schema)

    workflow.add_node("harvest_data", harvest_github_data)
    workflow.add_node("analyze_diffs", analyze_commit_churn)
    workflow.add_node("generate_summary", generate_insight_summary)

    workflow.set_entry_point("harvest_data")
    workflow.add_edge("harvest_data", "analyze_diffs")
    workflow.add_edge("analyze_diffs", "generate_summary")
    workflow.add_edge("generate_summary", END)

    return workflow.compile()
