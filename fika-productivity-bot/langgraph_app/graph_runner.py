# langgraph_app/graph_runner.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END
from langchain.tools import tool

from agents.data_harvester import harvest_data
from agents.diff_analyst import analyze_diff
from agents.insight_narrator import generate_insights


# 🧩 Define schema for state passed between graph nodes
class ReportState(TypedDict, total=False):
    data: Dict[str, Any]  # main payload passed between tools


from pydantic import BaseModel


# 🧩 LangGraph State
class ReportState(TypedDict, total=False):
    data: Dict[str, Any]


# 🧑‍🔧 Input types for tools
class DataInput(BaseModel):
    pass  # harvest_tool takes no input


class AnalysisInput(BaseModel):
    data: Dict[str, Any]


# 🌱 Step 1: Data Harvester Tool
@tool(args_schema=DataInput)
def harvest_tool() -> Dict:
    """Harvest raw GitHub event data from seed file."""
    return {"data": harvest_data()}


# 🔍 Step 2: Diff Analyst Tool
@tool(args_schema=AnalysisInput)
def diff_tool(data: Dict[str, Any]) -> Dict:
    """Analyze code churn and summarize metrics."""
    analysis = analyze_diff(data)
    return {"data": {
        **data,  # keep original raw commit data
        **analysis  # e.g., author_stats, ci_failures, etc.
    }}


# 🧠 Step 3: Insight Narrator Tool
@tool(args_schema=AnalysisInput)
def narrator_tool(data: Dict[str, Any]) -> Dict:
    """Generate a weekly engineering summary using DORA metrics."""
    summary = generate_insights(data)

    # Keep previous keys (e.g., author_stats) alongside headline/insights
    return {"data": {
        **data,
        **summary
    }}


# 🧠 LangGraph Orchestration
def build_graph():
    graph = StateGraph(ReportState)

    graph.add_node("harvester", harvest_tool)
    graph.add_node("analyst", diff_tool)
    graph.add_node("narrator", narrator_tool)

    graph.set_entry_point("harvester")
    graph.add_edge("harvester", "analyst")
    graph.add_edge("analyst", "narrator")
    graph.add_edge("narrator", END)

    return graph.compile()


# 🔁 Entry-point function to run the full pipeline
def run_productivity_report() -> Dict:
    graph = build_graph()
    result = graph.invoke({})
    return result


# 🧪 Local test
if __name__ == "__main__":
    report = run_productivity_report()
    print(report["headline"])
    print()
    print("\n".join(report["insights"]))
