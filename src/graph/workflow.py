"""LangGraph workflow orchestration for productivity intelligence agents."""
from datetime import datetime
from typing import Literal, Dict, Any
import uuid

from langgraph.graph import StateGraph, END

from .state import WorkflowState, create_initial_state, update_state_agent_transition
from ..agents.data_harvester import data_harvester
from ..agents.diff_analyst import diff_analyst
from ..agents.insight_narrator import insight_narrator
from ..config import logger, settings


class ProductivityWorkflow:
    """LangGraph workflow for engineering productivity analysis."""
    
    def __init__(self):
        self.graph = self._build_graph()
        # For MVP, we'll use simple in-memory state management
        # No checkpointing needed for the demo - keeps it simple
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("data_harvester", self._run_data_harvester)
        workflow.add_node("diff_analyst", self._run_diff_analyst)
        workflow.add_node("insight_narrator", self._run_insight_narrator)
        
        # Add edges (workflow flow)
        workflow.add_edge("data_harvester", "diff_analyst")
        workflow.add_edge("diff_analyst", "insight_narrator")
        workflow.add_edge("insight_narrator", END)
        
        # Set entry point
        workflow.set_entry_point("data_harvester")
        
        # Compile the graph (no checkpointing for simplicity)
        app = workflow.compile()
        
        logger.info("LangGraph workflow compiled successfully")
        return app
    
    def _run_data_harvester(self, state: WorkflowState) -> WorkflowState:
        """Execute the Data Harvester agent."""
        logger.info("Executing Data Harvester agent")
        
        try:
            # Update state to show current agent
            state["current_agent"] = "data_harvester"
            state["updated_at"] = datetime.now()
            
            # Run the agent
            updated_state = data_harvester.process(state)
            
            # Mark agent as completed and transition
            updated_state = update_state_agent_transition(
                updated_state, 
                "data_harvester", 
                "diff_analyst"
            )
            
            logger.info(f"Data Harvester completed: {updated_state['events_count']} events harvested")
            return updated_state
            
        except Exception as e:
            logger.error(f"Data Harvester failed: {e}")
            state["errors"].append(f"Data Harvester failed: {str(e)}")
            state["current_agent"] = "failed"
            return state
    
    def _run_diff_analyst(self, state: WorkflowState) -> WorkflowState:
        """Execute the Diff Analyst agent."""
        logger.info("Executing Diff Analyst agent")
        
        try:
            # Update state to show current agent
            state["current_agent"] = "diff_analyst"
            state["updated_at"] = datetime.now()
            
            # Check if we have data to analyze
            if not state.get("github_events"):
                error_msg = "No GitHub events available for analysis"
                logger.error(error_msg)
                state["errors"].append(error_msg)
                state["current_agent"] = "failed"
                return state
            
            # Run the agent
            updated_state = diff_analyst.process(state)
            
            # Mark agent as completed and transition
            updated_state = update_state_agent_transition(
                updated_state,
                "diff_analyst",
                "insight_narrator"
            )
            
            logger.info(f"Diff Analyst completed: {len(updated_state.get('diff_stats', []))} author analyses")
            return updated_state
            
        except Exception as e:
            logger.error(f"Diff Analyst failed: {e}")
            state["errors"].append(f"Diff Analyst failed: {str(e)}")
            state["current_agent"] = "failed"
            return state
    
    def _run_insight_narrator(self, state: WorkflowState) -> WorkflowState:
        """Execute the Insight Narrator agent."""
        logger.info("Executing Insight Narrator agent")
        
        try:
            # Update state to show current agent
            state["current_agent"] = "insight_narrator"
            state["updated_at"] = datetime.now()
            
            # Run the agent
            updated_state = insight_narrator.process(state)
            
            # Mark workflow as completed
            updated_state = update_state_agent_transition(
                updated_state,
                "insight_narrator",
                None  # No next agent - workflow complete
            )
            
            logger.info("Insight Narrator completed: narrative generated")
            return updated_state
            
        except Exception as e:
            logger.error(f"Insight Narrator failed: {e}")
            state["errors"].append(f"Insight Narrator failed: {str(e)}")
            state["current_agent"] = "failed"
            return state
    
    def run_analysis(
        self,
        repo_name: str,
        period_start: datetime,
        period_end: datetime,
        requested_by: str,
        command_params: dict = None
    ) -> WorkflowState:
        """Run the complete productivity analysis workflow."""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Create initial state
        initial_state = create_initial_state(
            request_id=request_id,
            repo_name=repo_name,
            period_start=period_start,
            period_end=period_end,
            requested_by=requested_by,
            command_params=command_params or {}
        )
        
        logger.info(f"Starting productivity analysis workflow for {repo_name} (request: {request_id})")
        
        try:
            # Run the workflow - simple invoke without checkpointing
            final_state = self.graph.invoke(initial_state)
            
            # Log completion
            if final_state.get("completed_at"):
                processing_time = final_state.get("processing_time_ms", 0)
                logger.info(f"Workflow completed successfully in {processing_time}ms")
            else:
                logger.warning("Workflow completed but may not have finished all steps")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
            initial_state["current_agent"] = "failed"
            return initial_state
    
    def get_workflow_status(self, request_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow execution."""
        # For the MVP, we'll track status in our database
        # This is a simplified implementation - in production you'd use persistent checkpointing
        return {
            "request_id": request_id,
            "status": "completed_or_not_found",
            "note": "Status tracking simplified for MVP - check database for results"
        }
    
    def list_recent_workflows(self, limit: int = 10) -> list:
        """List recent workflow executions."""
        # Simplified for MVP - could query database for recent analyses
        return []


# Global workflow instance
productivity_workflow = ProductivityWorkflow()


def run_productivity_analysis(
    repo_name: str = None,
    period_start: datetime = None,
    period_end: datetime = None,
    requested_by: str = "system",
    command_params: dict = None
) -> WorkflowState:
    """Convenience function to run productivity analysis."""
    
    # Use defaults if not provided
    repo_name = repo_name or f"{settings.default_repo_owner}/{settings.default_repo_name}"
    
    if not period_start:
        from datetime import timedelta
        period_end = period_end or datetime.now()
        period_start = period_end - timedelta(days=settings.default_lookback_days)
    
    return productivity_workflow.run_analysis(
        repo_name=repo_name,
        period_start=period_start,
        period_end=period_end,
        requested_by=requested_by,
        command_params=command_params
    )