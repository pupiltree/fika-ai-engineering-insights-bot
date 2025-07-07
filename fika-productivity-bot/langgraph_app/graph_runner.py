

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END
from langchain.tools import tool

from agents.data_harvester import harvest_data
from agents.diff_analyst import analyze_diff
from agents.insight_narrator import generate_insights



class ReportState(TypedDict, total=False):
    data: Dict[str, Any]  


from pydantic import BaseModel


class ReportState(TypedDict, total=False):
    data: Dict[str, Any]


class DataInput(BaseModel):
    pass  


class AnalysisInput(BaseModel):
    data: Dict[str, Any]


@tool(args_schema=DataInput)
def harvest_tool() -> Dict:
    
    return {"data": harvest_data()}



@tool(args_schema=AnalysisInput)
def diff_tool(data: Dict[str, Any]) -> Dict:
    
    analysis = analyze_diff(data)
    return {"data": {
        **data, 
        **analysis  
    }}



@tool(args_schema=AnalysisInput)
def narrator_tool(data: Dict[str, Any]) -> Dict:
    
    summary = generate_insights(data)

   
    return {"data": {
        **data,
        **summary
    }}



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



def run_productivity_report() -> Dict:
    graph = build_graph()
    result = graph.invoke({})
    return result



if __name__ == "__main__":
    report = run_productivity_report()
    print(report["headline"])
    print()
    print("\n".join(report["insights"]))
