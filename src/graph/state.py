"""LangGraph state management for agent workflow."""
from typing import TypedDict, List, Optional, Annotated
from datetime import datetime
import operator

from langchain_core.messages import BaseMessage

from ..data.models import GitHubEvent, DiffStats, DORAMetrics, AgentState


class WorkflowState(TypedDict):
    """State shared between agents in the LangGraph workflow."""
    
    # Request metadata
    request_id: str
    repo_name: str
    period_start: datetime
    period_end: datetime
    requested_by: str  # Slack user ID
    command_params: dict  # Original slash command parameters
    
    # Data pipeline - populated by Data Harvester
    github_events: Annotated[List[GitHubEvent], operator.add]
    events_count: int
    data_quality_score: float  # 0-1 score of data completeness
    
    # Analysis - populated by Diff Analyst
    diff_stats: Annotated[List[DiffStats], operator.add]
    dora_metrics: Optional[DORAMetrics]
    anomalies: Annotated[List[str], operator.add]  # Detected anomalies/outliers
    risk_factors: Annotated[List[str], operator.add]  # Code quality risks
    
    # Insights - populated by Insight Narrator
    narrative: Optional[str]
    executive_summary: Optional[str]
    actionable_insights: Annotated[List[str], operator.add]
    charts: Annotated[List[str], operator.add]  # File paths to generated charts
    
    # Workflow control
    current_agent: str
    completed_agents: Annotated[List[str], operator.add]
    next_agent: Optional[str]
    
    # Error handling
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]
    retry_count: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    processing_time_ms: Optional[int]
    
    # Agent-specific data (flexible dict for each agent's intermediate results)
    agent_data: dict


def create_initial_state(
    request_id: str,
    repo_name: str,
    period_start: datetime,
    period_end: datetime,
    requested_by: str,
    command_params: dict = None
) -> WorkflowState:
    """Create initial workflow state."""
    now = datetime.now()
    
    return WorkflowState(
        # Request metadata
        request_id=request_id,
        repo_name=repo_name,
        period_start=period_start,
        period_end=period_end,
        requested_by=requested_by,
        command_params=command_params or {},
        
        # Data pipeline
        github_events=[],
        events_count=0,
        data_quality_score=0.0,
        
        # Analysis
        diff_stats=[],
        dora_metrics=None,
        anomalies=[],
        risk_factors=[],
        
        # Insights
        narrative=None,
        executive_summary=None,
        actionable_insights=[],
        charts=[],
        
        # Workflow control
        current_agent="data_harvester",
        completed_agents=[],
        next_agent="data_harvester",
        
        # Error handling
        errors=[],
        warnings=[],
        retry_count=0,
        
        # Metadata
        created_at=now,
        updated_at=now,
        completed_at=None,
        processing_time_ms=None,
        
        # Agent-specific data
        agent_data={}
    )


def update_state_agent_transition(
    state: WorkflowState,
    current_agent: str,
    next_agent: Optional[str] = None
) -> WorkflowState:
    """Update state when transitioning between agents."""
    now = datetime.now()
    
    # Mark current agent as completed
    if current_agent not in state["completed_agents"]:
        state["completed_agents"].append(current_agent)
    
    # Update workflow control
    state["current_agent"] = next_agent or "completed"
    state["next_agent"] = next_agent
    state["updated_at"] = now
    
    # Mark as completed if no next agent
    if not next_agent:
        state["completed_at"] = now
        processing_time = (now - state["created_at"]).total_seconds() * 1000
        state["processing_time_ms"] = int(processing_time)
    
    return state


def add_error_to_state(state: WorkflowState, error_message: str) -> WorkflowState:
    """Add an error to the workflow state."""
    state["errors"].append(f"[{datetime.now().isoformat()}] {error_message}")
    state["updated_at"] = datetime.now()
    return state


def add_warning_to_state(state: WorkflowState, warning_message: str) -> WorkflowState:
    """Add a warning to the workflow state."""
    state["warnings"].append(f"[{datetime.now().isoformat()}] {warning_message}")
    state["updated_at"] = datetime.now()
    return state


def is_state_valid(state: WorkflowState) -> tuple[bool, List[str]]:
    """Validate workflow state integrity."""
    validation_errors = []
    
    # Check required fields
    required_fields = ["request_id", "repo_name", "period_start", "period_end"]
    for field in required_fields:
        if not state.get(field):
            validation_errors.append(f"Missing required field: {field}")
    
    # Check date logic
    if state.get("period_start") and state.get("period_end"):
        if state["period_start"] >= state["period_end"]:
            validation_errors.append("period_start must be before period_end")
    
    # Check workflow progression
    completed = state.get("completed_agents", [])
    current = state.get("current_agent")
    
    if current == "diff_analyst" and "data_harvester" not in completed:
        validation_errors.append("diff_analyst cannot run before data_harvester")
    
    if current == "insight_narrator" and "diff_analyst" not in completed:
        validation_errors.append("insight_narrator cannot run before diff_analyst")
    
    # Check data consistency
    if state.get("events_count", 0) != len(state.get("github_events", [])):
        validation_errors.append("events_count doesn't match github_events length")
    
    return len(validation_errors) == 0, validation_errors


def get_state_summary(state: WorkflowState) -> dict:
    """Get a summary of the current workflow state."""
    return {
        "request_id": state["request_id"],
        "repo_name": state["repo_name"],
        "current_agent": state["current_agent"],
        "completed_agents": state["completed_agents"],
        "events_count": state["events_count"],
        "has_analysis": state["dora_metrics"] is not None,
        "has_narrative": state["narrative"] is not None,
        "errors_count": len(state["errors"]),
        "warnings_count": len(state["warnings"]),
        "processing_time_ms": state.get("processing_time_ms"),
        "is_completed": state["completed_at"] is not None
    }