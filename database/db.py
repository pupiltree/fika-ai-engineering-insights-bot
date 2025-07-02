import os
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, func, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
import logging

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./github_insights.db")

if DATABASE_URL.startswith('postgresql+asyncpg'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')

if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    
    @event.listens_for(engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = SessionLocal.query_property()

class RepositoryMetrics(Base):
    __tablename__ = "repository_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    repository = Column(String, index=True)
    metrics = Column(JSON)
    report_type = Column(String, default="on-demand")
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RepositoryMetrics(repo={self.repository}, date={self.date})>"

def init_db():
    """Initialize the database by creating all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
