"""
Database module for the GitHub Insights Bot.

This module provides an optional PostgreSQL database backend for storing
and retrieving repository metrics. If no database is configured,
the application will continue to work with in-memory storage only.
"""

from .db import (
    init_db,
    get_db,
    RepositoryMetrics,
    Base,
    engine,
    SessionLocal
)

from .crud import (
    save_metrics,
    get_metrics,
    DBAccessError
)

__all__ = [
    'init_db',
    'get_db',
    'save_metrics',
    'get_metrics',
    'DBAccessError',
    'RepositoryMetrics',
    'Base',
    'engine',
    'SessionLocal'
]
