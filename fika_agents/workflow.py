from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from fika_agents.data_harvester import DataHarvester
from fika_agents.diff_analyst import DiffAnalyst
from fika_agents.insight_narrator import InsightNarrator

class WorkflowState(TypedDict):
    """State object for the LangGraph workflow"""
    github_data: Dict[str, Any]
    analysis: Dict[str, Any]
    narrative: str
    current_step: str

class FikaWorkflow:
    """
    LangGraph workflow that orchestrates DataHarvester -> DiffAnalyst -> InsightNarrator
    """
    
    def __init__(self):
        self.data_harvester = DataHarvester()
        self.diff_analyst = DiffAnalyst()
        self.insight_narrator = InsightNarrator()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("harvest_data", self._harvest_data_node)
        workflow.add_node("analyze_diff", self._analyze_diff_node)
        workflow.add_node("generate_narrative", self._generate_narrative_node)
        
        # Add edges
        workflow.add_edge("harvest_data", "analyze_diff")
        workflow.add_edge("analyze_diff", "generate_narrative")
        workflow.add_edge("generate_narrative", END)
        
        # Set entry point
        workflow.set_entry_point("harvest_data")
        
        return workflow.compile()
    
    def _harvest_data_node(self, state: WorkflowState) -> WorkflowState:
        """DataHarvester node"""
        github_data = self.data_harvester.fetch_data()
        return {
            **state,
            "github_data": github_data,
            "current_step": "data_harvested"
        }
    
    def _analyze_diff_node(self, state: WorkflowState) -> WorkflowState:
        """DiffAnalyst node"""
        analysis = self.diff_analyst.analyze(state["github_data"])
        return {
            **state,
            "analysis": analysis,
            "current_step": "analysis_complete"
        }
    
    def _generate_narrative_node(self, state: WorkflowState) -> WorkflowState:
        """InsightNarrator node"""
        narrative = self.insight_narrator.summarize(state["analysis"])
        return {
            **state,
            "narrative": narrative,
            "current_step": "narrative_complete"
        }
    
    def run_weekly_report(self) -> str:
        """Run the complete workflow and return the narrative summary"""
        initial_state = WorkflowState(
            github_data={},
            analysis={},
            narrative="",
            current_step="starting"
        )
        
        result = self.graph.invoke(initial_state)
        return result["narrative"]
    
    def get_analysis_data(self) -> Dict[str, Any]:
        """Run workflow and return analysis data"""
        initial_state = WorkflowState(
            github_data={},
            analysis={},
            narrative="",
            current_step="starting"
        )
        
        result = self.graph.invoke(initial_state)
        return result["analysis"] 