"""Data models for the Engineering Productivity MVP."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """GitHub event types we track."""
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    CI_RUN = "ci_run"


class MetricType(str, Enum):
    """Metric types we calculate."""
    COMMIT_COUNT = "commit_count"
    PR_COUNT = "pr_count"
    LINES_ADDED = "lines_added"
    LINES_DELETED = "lines_deleted"
    FILES_CHANGED = "files_changed"
    REVIEW_LATENCY = "review_latency"
    CYCLE_TIME = "cycle_time"
    CI_FAILURE_RATE = "ci_failure_rate"
    DEPLOYMENT_FREQUENCY = "deployment_frequency"
    LEAD_TIME = "lead_time"
    MTTR = "mttr"


class GitHubEvent(BaseModel):
    """Raw GitHub event data."""
    id: str
    repo_name: str
    event_type: EventType
    author: str
    timestamp: datetime
    raw_data: Dict[str, Any]
    
    # Parsed fields from raw_data
    additions: Optional[int] = None
    deletions: Optional[int] = None
    changed_files: Optional[int] = None
    pr_number: Optional[int] = None
    commit_sha: Optional[str] = None


class Metric(BaseModel):
    """Computed productivity metric."""
    id: Optional[int] = None
    repo_name: str
    author: str
    metric_type: MetricType
    value: float
    period: str  # e.g., "daily", "weekly", "monthly"
    timestamp: datetime


class DiffStats(BaseModel):
    """Code churn statistics."""
    author: str
    repo_name: str
    period_start: datetime
    period_end: datetime
    total_additions: int
    total_deletions: int
    total_files_changed: int
    commit_count: int
    churn_rate: float  # (additions + deletions) / total_lines
    files_per_commit: float


class DORAMetrics(BaseModel):
    """DORA four key metrics."""
    repo_name: str
    period_start: datetime
    period_end: datetime
    
    # Four Key Metrics
    lead_time_hours: Optional[float] = None  # Time from commit to production
    deployment_frequency: Optional[float] = None  # Deployments per day
    change_failure_rate: Optional[float] = None  # % of deployments causing failures
    mttr_hours: Optional[float] = None  # Mean time to recovery


class PromptLog(BaseModel):
    """Audit log for AI agent prompts and responses."""
    id: Optional[int] = None
    agent_name: str
    prompt: str
    response: str
    timestamp: datetime
    execution_time_ms: Optional[int] = None
    token_count: Optional[int] = None


class AgentState(BaseModel):
    """State shared between agents in LangGraph workflow."""
    request_id: str
    repo_name: str
    period_start: datetime
    period_end: datetime
    
    # Data collected by Data Harvester
    github_events: List[GitHubEvent] = Field(default_factory=list)
    
    # Analysis by Diff Analyst
    diff_stats: List[DiffStats] = Field(default_factory=list)
    dora_metrics: Optional[DORAMetrics] = None
    anomalies: List[str] = Field(default_factory=list)
    
    # Insights by Narrator
    narrative: Optional[str] = None
    charts: List[str] = Field(default_factory=list)  # File paths to generated charts
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SlackReport(BaseModel):
    """Formatted report for Slack delivery."""
    title: str
    summary: str
    narrative: str
    charts: List[str]  # URLs or file paths
    metrics_table: str  # Formatted table
    timestamp: datetime = Field(default_factory=datetime.now)