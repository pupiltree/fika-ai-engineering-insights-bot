import json
import sqlite3
from datetime import datetime, timedelta
import random

def generate_seed_data():
    """Generate realistic fake GitHub events for demo"""
    
    authors = ['alice', 'bob', 'charlie', 'diana', 'eve']
    
    commits = []
    base_date = datetime.now() - timedelta(days=7)
    
    for i in range(30):
        commit_date = base_date + timedelta(
            days=random.randint(0, 7),
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59)
        )
        
        author = random.choice(authors)
        additions = random.randint(10, 500)
        deletions = random.randint(5, additions // 2)
        files_changed = random.randint(1, 10)
        
        commit = {
            'sha': f'commit_{i:03d}_{random.randint(1000, 9999)}',
            'author': author,
            'author_email': f'{author}@company.com',
            'message': random.choice([
                'Add new feature implementation',
                'Fix critical bug in authentication',
                'Refactor database connection logic',
                'Update API documentation',
                'Improve error handling',
                'Add unit tests for user service',
                'Optimize query performance',
                'Update dependencies',
                'Fix memory leak issue',
                'Add logging for debugging'
            ]),
            'date': commit_date.isoformat() + 'Z',
            'additions': additions,
            'deletions': deletions,
            'total': additions + deletions,
            'files_changed': files_changed
        }
        
        commits.append(commit)
    
    # Save to database
    conn = sqlite3.connect('fika.db')
    c = conn.cursor()
    
    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS commits 
                 (sha TEXT PRIMARY KEY, author TEXT, message TEXT, 
                  date TEXT, additions INTEGER, deletions INTEGER, 
                  total INTEGER, files_changed INTEGER)''')
    
    # Insert seed data
    for commit in commits:
        c.execute('''INSERT OR REPLACE INTO commits 
                   (sha, author, message, date, additions, deletions, total, files_changed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (commit['sha'], commit['author'], commit['message'], 
                  commit['date'], commit['additions'], commit['deletions'],
                  commit['total'], commit['files_changed']))
    
    conn.commit()
    conn.close()
    
    # Also save as JSON for reference
    with open('seed_data.json', 'w') as f:
        json.dump(commits, f, indent=2)
    
    print(f"✅ Generated {len(commits)} seed commits")
    return commits

if __name__ == "__main__":
    generate_seed_data()
