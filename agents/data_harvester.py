import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import os

class DataHarvesterAgent:
    """Simple GitHub data harvester without Pydantic dependencies"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {'Authorization': f'token {github_token}'} if github_token else {}
        self.name = "DataHarvester"
        print(f"🔧 {self.name} initialized with token: {'✅ Yes' if github_token else '❌ No'}")
    
    def run(self, repo: str) -> Dict:
        print(f"🔍 {self.name}: Fetching data for {repo}")
        data = self.fetch_github_data(repo)
        self.save_to_db(data)
        return data
    
    def fetch_github_data(self, repo: str) -> Dict:
        """Fetch real GitHub data with proper error handling"""
        
        if not self.github_token:
            print("⚠️ No GitHub token found - using fallback data")
            return self.get_fallback_data(repo)
        
        try:
            print(f"🌐 Attempting to fetch real data from GitHub API for {repo}")
            
            # Test API connection first
            test_url = "https://api.github.com/rate_limit"
            test_response = requests.get(test_url, headers=self.headers, timeout=10)
            
            if test_response.status_code != 200:
                print(f"❌ GitHub API test failed: {test_response.status_code}")
                return self.get_fallback_data(repo)
            
            rate_info = test_response.json()
            print(f"✅ GitHub API connected. Rate limit: {rate_info['rate']['remaining']}/{rate_info['rate']['limit']}")
            
            # Fetch commits
            commits_url = f'https://api.github.com/repos/{repo}/commits'
            commits_response = requests.get(commits_url, headers=self.headers, timeout=15)
            
            if commits_response.status_code == 200:
                commits = commits_response.json()[:15]  # Get 15 recent commits
                processed_commits = []
                
                print(f"📥 Found {len(commits)} commits, processing...")
                
                for i, commit in enumerate(commits):
                    try:
                        commit_detail = self.get_commit_stats(repo, commit['sha'])
                        if commit_detail:
                            processed_commits.append(commit_detail)
                            print(f"✅ Processed commit {i+1}/{len(commits)}")
                        else:
                            print(f"⚠️ Skipped commit {i+1}/{len(commits)}")
                    except Exception as e:
                        print(f"❌ Error processing commit {i+1}: {e}")
                        continue
                
                if processed_commits:
                    result = {
                        'commits': processed_commits,
                        'repo': repo,
                        'fetched_at': datetime.now().isoformat(),
                        'source': 'github_api',
                        'total_commits': len(processed_commits)
                    }
                    print(f"🎉 Successfully fetched {len(processed_commits)} real commits from {repo}")
                    return result
            
            else:
                print(f"❌ GitHub API error: {commits_response.status_code} - {commits_response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("⏰ GitHub API timeout - using fallback data")
        except requests.exceptions.ConnectionError:
            print("🌐 GitHub API connection error - using fallback data")
        except Exception as e:
            print(f"❌ Unexpected GitHub API error: {e}")
        
        # Fallback to mock data
        print("🔄 Falling back to high-quality mock data")
        return self.get_fallback_data(repo)
    
    def get_commit_stats(self, repo: str, sha: str) -> Optional[Dict]:
        """Get detailed commit statistics"""
        try:
            url = f'https://api.github.com/repos/{repo}/commits/{sha}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                commit = response.json()
                
                # Safely extract stats
                stats = commit.get('stats', {})
                files = commit.get('files', [])
                
                return {
                    'sha': sha[:8],  # Short SHA
                    'author': commit['commit']['author']['name'],
                    'author_email': commit['commit']['author']['email'],
                    'message': commit['commit']['message'][:150] + ('...' if len(commit['commit']['message']) > 150 else ''),
                    'date': commit['commit']['author']['date'],
                    'additions': stats.get('additions', 0),
                    'deletions': stats.get('deletions', 0),
                    'total': stats.get('total', 0),
                    'files_changed': len(files)
                }
            else:
                print(f"⚠️ Commit detail fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching commit {sha[:8]}: {e}")
            return None
    
    def get_fallback_data(self, repo: str) -> Dict:
        """High-quality realistic fallback data"""
        authors = ['alice_dev', 'bob_engineer', 'charlie_lead', 'diana_qa', 'eve_devops']
        
        commits = []
        base_date = datetime.now() - timedelta(days=14)
        
        commit_messages = [
            "Implement OAuth 2.0 authentication flow",
            "Fix memory leak in connection pooling",
            "Add comprehensive error handling for API calls",
            "Refactor database schema for better performance",
            "Update dependencies to latest stable versions",
            "Add unit tests for user management service",
            "Optimize SQL queries for dashboard analytics",
            "Fix race condition in concurrent request handling",
            "Implement caching layer for frequently accessed data",
            "Add monitoring and alerting for production systems",
            "Refactor legacy code to use modern patterns",
            "Fix security vulnerability in input validation",
            "Add support for real-time notifications",
            "Optimize frontend bundle size and loading times",
            "Implement automated backup and recovery system"
        ]
        
        for i in range(15):
            commit_date = base_date + timedelta(
                days=i,
                hours=random.randint(9, 18),
                minutes=random.randint(0, 59)
            )
            
            author = random.choice(authors)
            message = random.choice(commit_messages)
            
            # Realistic code churn patterns
            if 'refactor' in message.lower() or 'optimize' in message.lower():
                additions = random.randint(100, 400)
                deletions = random.randint(80, 300)
            elif 'fix' in message.lower():
                additions = random.randint(20, 100)
                deletions = random.randint(10, 50)
            elif 'add' in message.lower() or 'implement' in message.lower():
                additions = random.randint(150, 500)
                deletions = random.randint(5, 30)
            else:
                additions = random.randint(50, 200)
                deletions = random.randint(10, 80)
            
            files_changed = min(random.randint(1, 12), additions // 30 + 1)
            
            commit = {
                'sha': f'mock_{i:03d}_{random.randint(1000, 9999)}',
                'author': author,
                'author_email': f'{author}@{repo.split("/")[0] if "/" in repo else "company"}.com',
                'message': message,
                'date': commit_date.isoformat() + 'Z',
                'additions': additions,
                'deletions': deletions,
                'total': additions + deletions,
                'files_changed': files_changed
            }
            
            commits.append(commit)
        
        return {
            'commits': commits,
            'repo': repo,
            'fetched_at': datetime.now().isoformat(),
            'source': 'fallback_data',
            'total_commits': len(commits)
        }
    
    def save_to_db(self, data: Dict):
        """Save commits to database"""
        try:
            conn = sqlite3.connect('fika.db')
            c = conn.cursor()
            
            # Create table if not exists
            c.execute('''CREATE TABLE IF NOT EXISTS commits 
                         (sha TEXT PRIMARY KEY, author TEXT, message TEXT, 
                          date TEXT, additions INTEGER, deletions INTEGER, 
                          total INTEGER, files_changed INTEGER, repo TEXT)''')
            
            saved_count = 0
            for commit in data['commits']:
                try:
                    c.execute('''INSERT OR REPLACE INTO commits 
                               (sha, author, message, date, additions, deletions, total, files_changed, repo)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (commit['sha'], commit['author'], commit['message'], 
                              commit['date'], commit['additions'], commit['deletions'],
                              commit['total'], commit['files_changed'], data['repo']))
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Error saving commit {commit['sha']}: {e}")
            
            conn.commit()
            conn.close()
            print(f"💾 Saved {saved_count}/{len(data['commits'])} commits to database")
            
        except Exception as e:
            print(f"❌ Database save error: {e}")

# Import random for fallback data
import random
