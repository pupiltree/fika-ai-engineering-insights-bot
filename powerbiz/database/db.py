"""
Database configuration and session management for PowerBiz
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from powerbiz.database.models import Base

# Get database URL from environment variables or use SQLite as default
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///powerbiz.db')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db():
    """Initialize the database."""
    # Create all tables
    Base.metadata.create_all(engine)
    
def get_session():
    """Get a database session."""
    return Session()

def close_session(session):
    """Close a database session."""
    session.close()
