import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

DATABASE_NAME = "fika_ai_insights.db"

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create commits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commit_hash TEXT UNIQUE NOT NULL,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            additions INTEGER DEFAULT 0,
            deletions INTEGER DEFAULT 0,
            changed_files INTEGER DEFAULT 0
        )
    ''')
    
    # Create pull_requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pull_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr_number INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            merged_at DATETIME,
            additions INTEGER DEFAULT 0,
            deletions INTEGER DEFAULT 0,
            changed_files INTEGER DEFAULT 0,
            status TEXT DEFAULT 'open'
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' initialized successfully!")

def init_db():
    """Alias for init_database() for backward compatibility"""
    return init_database()

def insert_commit(commit_hash: str, author: str, message: str, timestamp: str, 
                 additions: int = 0, deletions: int = 0, changed_files: int = 0):
    """Insert a commit into the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO commits (commit_hash, author, message, timestamp, additions, deletions, changed_files)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (commit_hash, author, message, timestamp, additions, deletions, changed_files))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Commit already exists
    finally:
        conn.close()

def insert_pull_request(pr_number: int, title: str, author: str, created_at: str,
                       merged_at: str = None, additions: int = 0, deletions: int = 0,
                       changed_files: int = 0, status: str = 'open'):
    """Insert a pull request into the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO pull_requests (pr_number, title, author, created_at, merged_at, 
                                     additions, deletions, changed_files, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pr_number, title, author, created_at, merged_at, additions, deletions, changed_files, status))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # PR already exists
    finally:
        conn.close()

def fetch_commits() -> List[Dict[str, Any]]:
    """Fetch all commits from the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM commits ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    commits = []
    for row in rows:
        commits.append({
            'id': row[0],
            'commit_hash': row[1],
            'author': row[2],
            'message': row[3],
            'timestamp': row[4],
            'additions': row[5],
            'deletions': row[6],
            'changed_files': row[7]
        })
    
    conn.close()
    return commits

def fetch_pull_requests() -> List[Dict[str, Any]]:
    """Fetch all pull requests from the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pull_requests ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    prs = []
    for row in rows:
        prs.append({
            'id': row[0],
            'pr_number': row[1],
            'title': row[2],
            'author': row[3],
            'created_at': row[4],
            'merged_at': row[5],
            'additions': row[6],
            'deletions': row[7],
            'changed_files': row[8],
            'status': row[9]
        })
    
    conn.close()
    return prs

def get_database_stats() -> Dict[str, int]:
    """Get basic statistics about the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM commits')
    commit_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM pull_requests')
    pr_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_commits': commit_count,
        'total_prs': pr_count
    } 