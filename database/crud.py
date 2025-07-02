from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from .db import SessionLocal, RepositoryMetrics

Session = SessionLocal

class DBAccessError(Exception):
    """Custom exception for database access errors"""
    pass

def save_metrics(
    repository: str,
    metrics: Dict[str, Any],
    report_type: str = "on-demand"
) -> RepositoryMetrics:
    """
    Save repository metrics to the database
    
    Args:
        repository: Name of the repository
        metrics: Dictionary of metrics to save
        report_type: Type of report (default: "on-demand")
        
    Returns:
        The created RepositoryMetrics object
    """
    db = SessionLocal()
    try:
        db_metrics = RepositoryMetrics(
            repository=repository,
            metrics=metrics,
            report_type=report_type
        )
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        return db_metrics
    except Exception as e:
        db.rollback()
        raise DBAccessError(f"Failed to save metrics: {str(e)}")
    finally:
        db.close()

def get_metrics(
    repository: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    report_type: str = None,
    limit: int = 100
) -> List[RepositoryMetrics]:
    """
    Retrieve metrics from the database
    
    Args:
        repository: Filter by repository name
        start_date: Filter by start date
        end_date: Filter by end date
        report_type: Filter by report type
        limit: Maximum number of results to return
        
    Returns:
        List of matching RepositoryMetrics objects
    """
    db = SessionLocal()
    try:
        query = db.query(RepositoryMetrics)
        
        if repository:
            query = query.filter(RepositoryMetrics.repository == repository)
        if start_date:
            query = query.filter(RepositoryMetrics.date >= start_date)
        if end_date:
            query = query.filter(RepositoryMetrics.date <= end_date)
        if report_type:
            query = query.filter(RepositoryMetrics.report_type == report_type)
            
        return query.order_by(RepositoryMetrics.date.desc()).limit(limit).all()
    except Exception as e:
        raise DBAccessError(f"Failed to retrieve metrics: {str(e)}")
    finally:
        db.close()
