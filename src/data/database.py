"""SQLite database layer for the Engineering Productivity MVP."""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..config import settings, logger
from .models import GitHubEvent, Metric, PromptLog, EventType, MetricType


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS github_events (
                    id TEXT PRIMARY KEY,
                    repo_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    author TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT NOT NULL,
                    additions INTEGER,
                    deletions INTEGER,
                    changed_files INTEGER,
                    pr_number INTEGER,
                    commit_sha TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_name TEXT NOT NULL,
                    author TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    period TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    execution_time_ms INTEGER,
                    token_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_github_events_repo_timestamp 
                ON github_events(repo_name, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_repo_author_timestamp 
                ON metrics(repo_name, author, timestamp)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def insert_github_event(self, event: GitHubEvent) -> bool:
        """Insert a GitHub event into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO github_events 
                    (id, repo_name, event_type, author, timestamp, raw_data, 
                     additions, deletions, changed_files, pr_number, commit_sha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id,
                    event.repo_name,
                    event.event_type.value,
                    event.author,
                    event.timestamp,
                    json.dumps(event.raw_data),
                    event.additions,
                    event.deletions,
                    event.changed_files,
                    event.pr_number,
                    event.commit_sha
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting GitHub event: {e}")
            return False
    
    def get_github_events(
        self, 
        repo_name: str, 
        start_date: datetime, 
        end_date: datetime,
        event_type: Optional[EventType] = None,
        author: Optional[str] = None
    ) -> List[GitHubEvent]:
        """Retrieve GitHub events from the database."""
        query = """
            SELECT id, repo_name, event_type, author, timestamp, raw_data,
                   additions, deletions, changed_files, pr_number, commit_sha
            FROM github_events 
            WHERE repo_name = ? AND timestamp BETWEEN ? AND ?
        """
        params = [repo_name, start_date, end_date]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        
        if author:
            query += " AND author = ?"
            params.append(author)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                events = []
                for row in cursor.fetchall():
                    events.append(GitHubEvent(
                        id=row[0],
                        repo_name=row[1],
                        event_type=EventType(row[2]),
                        author=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        raw_data=json.loads(row[5]),
                        additions=row[6],
                        deletions=row[7],
                        changed_files=row[8],
                        pr_number=row[9],
                        commit_sha=row[10]
                    ))
                return events
        except Exception as e:
            logger.error(f"Error retrieving GitHub events: {e}")
            return []
    
    def insert_metric(self, metric: Metric) -> bool:
        """Insert a computed metric into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO metrics 
                    (repo_name, author, metric_type, value, period, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metric.repo_name,
                    metric.author,
                    metric.metric_type.value,
                    metric.value,
                    metric.period,
                    metric.timestamp
                ))
                metric.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting metric: {e}")
            return False
    
    def get_metrics(
        self,
        repo_name: str,
        start_date: datetime,
        end_date: datetime,
        metric_type: Optional[MetricType] = None,
        author: Optional[str] = None
    ) -> List[Metric]:
        """Retrieve metrics from the database."""
        query = """
            SELECT id, repo_name, author, metric_type, value, period, timestamp
            FROM metrics 
            WHERE repo_name = ? AND timestamp BETWEEN ? AND ?
        """
        params = [repo_name, start_date, end_date]
        
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type.value)
        
        if author:
            query += " AND author = ?"
            params.append(author)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                metrics = []
                for row in cursor.fetchall():
                    metrics.append(Metric(
                        id=row[0],
                        repo_name=row[1],
                        author=row[2],
                        metric_type=MetricType(row[3]),
                        value=row[4],
                        period=row[5],
                        timestamp=datetime.fromisoformat(row[6])
                    ))
                return metrics
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return []
    
    def log_prompt(self, log: PromptLog) -> bool:
        """Log an AI agent prompt and response."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO prompt_logs 
                    (agent_name, prompt, response, timestamp, execution_time_ms, token_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    log.agent_name,
                    log.prompt,
                    log.response,
                    log.timestamp,
                    log.execution_time_ms,
                    log.token_count
                ))
                log.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging prompt: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Count events
                cursor = conn.execute("SELECT COUNT(*) FROM github_events")
                stats['total_events'] = cursor.fetchone()[0]
                
                # Count metrics
                cursor = conn.execute("SELECT COUNT(*) FROM metrics")
                stats['total_metrics'] = cursor.fetchone()[0]
                
                # Count prompt logs
                cursor = conn.execute("SELECT COUNT(*) FROM prompt_logs")
                stats['total_prompt_logs'] = cursor.fetchone()[0]
                
                # Latest event
                cursor = conn.execute("""
                    SELECT timestamp FROM github_events 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                result = cursor.fetchone()
                stats['latest_event'] = result[0] if result else None
                
                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# Global database instance
db = Database()