from langgraph.graph import StateGraph, END
from typing import Dict, Any
from agents.data_harvester import DataHarvesterAgent
from agents.diff_analyst import DiffAnalystAgent
from agents.insight_narrator import InsightNarratorAgent
import os

class WorkflowState:
    def __init__(self):
        self.github_data = {}
        self.analysis_data = {}
        self.insights = {}
        self.repo = ""

def create_workflow():
    # Initialize agents
    harvester = DataHarvesterAgent(os.environ.get("GITHUB_TOKEN"))
    analyst = DiffAnalystAgent()
    narrator = InsightNarratorAgent()
    
    def harvest_data(state: Dict[str, Any]) -> Dict[str, Any]:
        repo = state.get('repo', 'microsoft/vscode')  # Default repo
        github_data = harvester.run(repo)
        return {"github_data": github_data, **state}
    
    def analyze_data(state: Dict[str, Any]) -> Dict[str, Any]:
        github_data = state.get('github_data', {})
        analysis_data = analyst.run(github_data)
        return {"analysis_data": analysis_data, **state}
    
    def generate_insights(state: Dict[str, Any]) -> Dict[str, Any]:
        github_data = state.get('github_data', {})
        analysis_data = state.get('analysis_data', {})
        insights = narrator.run(github_data, analysis_data)
        return {"insights": insights, **state}
    
    # Create workflow with proper state schema
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("harvester", harvest_data)
    workflow.add_node("analyst", analyze_data)
    workflow.add_node("narrator", generate_insights)
    
    # Add edges
    workflow.add_edge("harvester", "analyst")
    workflow.add_edge("analyst", "narrator")
    workflow.add_edge("narrator", END)
    
    # Set entry point
    workflow.set_entry_point("harvester")
    
    return workflow.compile()

def run_workflow(repo: str = "microsoft/vscode") -> Dict:
    workflow = create_workflow()
    
    initial_state = {"repo": repo}
    result = workflow.invoke(initial_state)
    
    return result