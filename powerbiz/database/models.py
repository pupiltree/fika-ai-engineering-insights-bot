"""
Database models for PowerBiz Developer Analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Developer(Base):
    """Developer model for storing engineer information."""
    __tablename__ = 'developers'

    id = Column(Integer, primary_key=True)
    github_username = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    email = Column(String(255))
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="developers")
    commits = relationship("Commit", back_populates="developer")
    pull_requests = relationship("PullRequest", back_populates="author")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Team(Base):
    """Team model for storing team/squad information."""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    developers = relationship("Developer", back_populates="team")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Repository(Base):
    """Repository model for storing GitHub repository information."""
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    commits = relationship("Commit", back_populates="repository")
    pull_requests = relationship("PullRequest", back_populates="repository")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Commit(Base):
    """Commit model for storing GitHub commit information."""
    __tablename__ = 'commits'

    id = Column(Integer, primary_key=True)
    sha = Column(String(40), unique=True, nullable=False)
    message = Column(Text)
    developer_id = Column(Integer, ForeignKey('developers.id'), nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # Commit statistics
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    changed_files = Column(Integer, default=0)
    
    # Relationships
    developer = relationship("Developer", back_populates="commits")
    repository = relationship("Repository", back_populates="commits")
    
    commit_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class PullRequest(Base):
    """Pull Request model for storing GitHub PR information."""
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey('developers.id'), nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # PR statistics
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    changed_files = Column(Integer, default=0)
    
    # PR state
    state = Column(String(20), nullable=False)  # open, closed, merged
    is_merged = Column(Boolean, default=False)
    
    # Review statistics
    review_count = Column(Integer, default=0)
    
    # DORA metrics related
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Lead time calculation (time between PR creation and merge)
    lead_time_minutes = Column(Float, nullable=True)
    
    # Relationships
    author = relationship("Developer", back_populates="pull_requests")
    repository = relationship("Repository", back_populates="pull_requests")
    reviews = relationship("Review", back_populates="pull_request")


class Review(Base):
    """Review model for storing PR review information."""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    pull_request_id = Column(Integer, ForeignKey('pull_requests.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('developers.id'), nullable=False)
    
    # Review state
    state = Column(String(20), nullable=False)  # APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
    
    # Review timing
    submitted_at = Column(DateTime, nullable=False)
    
    # Relationships
    pull_request = relationship("PullRequest", back_populates="reviews")
    reviewer = relationship("Developer")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class CIBuild(Base):
    """CI Build model for tracking CI/CD pipeline information."""
    __tablename__ = 'ci_builds'

    id = Column(Integer, primary_key=True)
    external_id = Column(String(40), unique=True)
    pull_request_id = Column(Integer, ForeignKey('pull_requests.id'), nullable=True)
    commit_sha = Column(String(40), nullable=False)
    
    # Build state
    status = Column(String(20), nullable=False)  # success, failure, pending, etc.
    
    # Build timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Build duration in seconds
    duration_seconds = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Deployment(Base):
    """Deployment model for tracking production deployments."""
    __tablename__ = 'deployments'

    id = Column(Integer, primary_key=True)
    external_id = Column(String(40), unique=True, nullable=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # The commit that was deployed
    commit_sha = Column(String(40), nullable=False)
    
    # Deployment state
    status = Column(String(20), nullable=False)  # success, failure, pending, etc.
    environment = Column(String(50), nullable=False)  # production, staging, etc.
    
    # Deployment timing
    deployed_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Incident(Base):
    """Incident model for tracking production issues (for MTTR)."""
    __tablename__ = 'incidents'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # Potentially related to a specific deployment
    deployment_id = Column(Integer, ForeignKey('deployments.id'), nullable=True)
    
    # Incident timing
    detected_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # MTTR calculation (time to resolve) in minutes
    resolution_time_minutes = Column(Float, nullable=True)
    
    severity = Column(String(20), nullable=True)  # critical, high, medium, low
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class PromptLog(Base):
    """Log of all prompts and responses for auditability."""
    __tablename__ = 'prompt_logs'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50), nullable=False)  # data_harvester, diff_analyst, insight_narrator
    prompt_type = Column(String(50), nullable=False)
    prompt_content = Column(Text, nullable=False)
    response_content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
