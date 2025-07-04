"""
LangGraph workflow for PowerBiz Developer Analytics
"""

import logging
from typing import Dict, Any, List, TypedDict, Optional, Annotated, Literal
from datetime import datetime, timedelta

from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from powerbiz.agents.data_harvester import DataHarvesterAgent
from powerbiz.agents.diff_analyst import DiffAnalystAgent
from powerbiz.agents.insight_narrator import InsightNarratorAgent
from powerbiz.database.db import get_session
from powerbiz.database.models import Repository

logger = logging.getLogger(__name__)

# Define state types for the graph
class AgentState(TypedDict):
    """State passed between agents."""
    repository_id: int
    repository_name: str
    report_type: str  # "daily", "weekly", "monthly"
    date: Optional[str]
    data: Dict[str, Any]
    insights: Dict[str, Any]
    narrative: Dict[str, Any]
    error: Optional[str]

# Define the agent workflow
class EngineeringReportWorkflow:
    """Workflow for generating engineering reports using LangGraph."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.data_harvester = DataHarvesterAgent()
        self.diff_analyst = DiffAnalystAgent()
        self.insight_narrator = InsightNarratorAgent()
        
        # Define the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow.
        
        Returns:
            StateGraph: The workflow graph
        """
        # Define the graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("data_harvester", self.data_harvester_node)
        graph.add_node("diff_analyst", self.diff_analyst_node)
        graph.add_node("insight_narrator", self.insight_narrator_node)
        
        # Define edges
        graph.add_edge(START, "data_harvester")
        graph.add_edge("data_harvester", "diff_analyst")
        graph.add_edge("diff_analyst", "insight_narrator")
        graph.add_edge("insight_narrator", END)
        
        # Add conditional edges for error handling
        graph.add_conditional_edges(
            "data_harvester",
            self.check_for_errors,
            {
                "error": END,
                "continue": "diff_analyst",
            }
        )
        
        graph.add_conditional_edges(
            "diff_analyst",
            self.check_for_errors,
            {
                "error": END,
                "continue": "insight_narrator",
            }
        )
        
        return graph
    
    async def data_harvester_node(self, state: AgentState) -> AgentState:
        """Data harvester node in the workflow.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            logger.info(f"Data harvester processing repository: {state['repository_name']}")
            
            # Get repository from database
            session = get_session()
            try:
                repository = session.query(Repository).get(state["repository_id"])
                
                if not repository:
                    return {
                        **state,
                        "error": f"Repository ID {state['repository_id']} not found"
                    }
                
                # Split repository name
                owner, repo = repository.full_name.split("/")
                
                # Set time range based on report type
                days_back = 1
                if state["report_type"] == "weekly":
                    days_back = 7
                elif state["report_type"] == "monthly":
                    days_back = 30
                
                # Analyze repository data
                data = await self.data_harvester.analyze_repository_data(
                    owner, repo, days_back=days_back
                )
                
                # Update state
                return {
                    **state,
                    "data": data
                }
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error in data harvester: {e}")
            return {
                **state,
                "error": f"Data harvester error: {str(e)}"
            }
    
    async def diff_analyst_node(self, state: AgentState) -> AgentState:
        """Diff analyst node in the workflow.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            logger.info(f"Diff analyst processing repository: {state['repository_name']}")
            
            # Set time range based on report type
            days_back = 1
            if state["report_type"] == "weekly":
                days_back = 7
            elif state["report_type"] == "monthly":
                days_back = 30
            
            # Analyze code churn
            code_churn = await self.diff_analyst.analyze_code_churn(
                state["repository_id"], days_back=days_back
            )
            
            # Analyze defect risk
            defect_risk = await self.diff_analyst.analyze_defect_risk(
                state["repository_id"], days_back=days_back
            )
            
            # Update state
            return {
                **state,
                "insights": {
                    "code_churn": code_churn,
                    "defect_risk": defect_risk
                }
            }
        except Exception as e:
            logger.error(f"Error in diff analyst: {e}")
            return {
                **state,
                "error": f"Diff analyst error: {str(e)}"
            }
    
    async def insight_narrator_node(self, state: AgentState) -> AgentState:
        """Insight narrator node in the workflow.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            logger.info(f"Insight narrator processing repository: {state['repository_name']}")
            
            # Generate report based on type
            if state["report_type"] == "daily":
                # Parse date if provided
                date = None
                if state.get("date"):
                    date = datetime.fromisoformat(state["date"])
                
                report = await self.insight_narrator.generate_daily_report(
                    state["repository_id"], date=date
                )
            elif state["report_type"] == "weekly":
                # Parse date if provided
                end_date = None
                if state.get("date"):
                    end_date = datetime.fromisoformat(state["date"])
                
                report = await self.insight_narrator.generate_weekly_report(
                    state["repository_id"], end_date=end_date
                )
            else:
                return {
                    **state,
                    "error": f"Unsupported report type: {state['report_type']}"
                }
            
            # Update state
            return {
                **state,
                "narrative": report
            }
        except Exception as e:
            logger.error(f"Error in insight narrator: {e}")
            return {
                **state,
                "error": f"Insight narrator error: {str(e)}"
            }
    
    def check_for_errors(self, state: AgentState) -> Literal["error", "continue"]:
        """Check if there are errors in the state.
        
        Args:
            state: Current workflow state
            
        Returns:
            "error" if there are errors, "continue" otherwise
        """
        if state.get("error"):
            return "error"
        return "continue"
    
    async def run_report_workflow(
        self,
        repository_id: int,
        report_type: str,
        date: Optional[str] = None
    ) -> AgentState:
        """Run the engineering report workflow.
        
        Args:
            repository_id: Database ID of the repository
            report_type: Type of report ("daily", "weekly", "monthly")
            date: Optional date for the report (ISO format)
            
        Returns:
            Final workflow state
        """
        # Get repository name
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            if not repository:
                raise ValueError(f"Repository ID {repository_id} not found")
            
            repository_name = repository.full_name
        finally:
            session.close()
        
        # Initialize state
        initial_state: AgentState = {
            "repository_id": repository_id,
            "repository_name": repository_name,
            "report_type": report_type,
            "date": date,
            "data": {},
            "insights": {},
            "narrative": {},
            "error": None
        }
        
        # Run the workflow
        final_state = await self.graph.arun(initial_state)
        
        return final_state
