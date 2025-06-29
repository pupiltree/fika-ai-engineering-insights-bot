import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    # Events table
    c.execute('''CREATE TABLE IF NOT EXISTS events 
                 (id TEXT PRIMARY KEY, type TEXT, actor TEXT, 
                  created_at TEXT, repo TEXT, data TEXT)''')
    
    # Commits table
    c.execute('''CREATE TABLE IF NOT EXISTS commits 
                 (sha TEXT PRIMARY KEY, author TEXT, message TEXT, 
                  date TEXT, additions INTEGER, deletions INTEGER, 
                  total INTEGER, files_changed INTEGER)''')
    
    # Metrics table
    c.execute('''CREATE TABLE IF NOT EXISTS metrics 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, metric_type TEXT, value REAL, data TEXT)''')
    
    # Workflow logs table
    c.execute('''CREATE TABLE IF NOT EXISTS workflow_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, agent TEXT, input_data TEXT, 
                  output_data TEXT, status TEXT)''')
    
    conn.commit()
    conn.close()

def save_workflow_log(agent: str, input_data: dict, output_data: dict, status: str = "success"):
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO workflow_logs 
                 (timestamp, agent, input_data, output_data, status)
                 VALUES (?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(), agent, 
               json.dumps(input_data), json.dumps(output_data), status))
    
    conn.commit()
    conn.close()

def get_recent_metrics(limit=10):
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM metrics ORDER BY date DESC LIMIT ?', (limit,))
    metrics = c.fetchall()
    
    conn.close()
    return metrics
