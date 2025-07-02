from github import Github
from datetime import datetime, timedelta
import os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def data_harvester_node(state):  
    print("\n [DataHarvesterAgent] Fetching GitHub data...")

    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    since = datetime.utcnow() - timedelta(days=30)

    g = Github(token)
    repo = g.get_repo(repo_name)
    commits = repo.get_commits(since=since)

    result = []
    file_changes = defaultdict(int)
    pull_requests = []
    
    for commit in commits:
        if commit.author:
            commit_data = {
                "author": commit.author.login,
                "message": commit.commit.message,
                "date": str(commit.commit.author.date),
                "additions": commit.stats.additions,
                "deletions": commit.stats.deletions,
                "total": commit.stats.total,
                "sha": commit.sha,
                "hour": commit.commit.author.date.hour,
                "day_of_week": commit.commit.author.date.strftime('%A'),
                "files_changed": [],
                "is_large_commit": commit.stats.total > 500,
                "is_late_commit": commit.commit.author.date.hour >= 20 or commit.commit.author.date.hour <= 6,
                "commit_type": classify_commit_type(commit.commit.message),
                "files_count": sum(1 for _ in commit.files) if commit.files else 0,
                "pull_request": None
            }
            
            # Try to get associated pull request
            try:
                prs = commit.get_pulls()
                if prs.totalCount > 0:
                    pr = prs[0]  # Get the first PR associated with this commit
                    pr_data = {
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "created_at": str(pr.created_at),
                        "merged_at": str(pr.merged_at) if pr.merged_at else None,
                        "reviewers": [reviewer.login for reviewer in pr.requested_reviewers],
                        "review_comments": pr.review_comments,
                        "labels": [label.name for label in pr.labels],
                        "review_status": pr.merged and "merged" or pr.state,
                        "author": commit.author.login  # Add author from commit
                    }
                    commit_data["pull_request"] = pr_data
                    pull_requests.append(pr_data)
            except Exception as e:
                print(f" Could not fetch PR details for commit {commit.sha[:8]}: {e}")
            
            try:
                for file in commit.files[:5]:  
                    if file.filename:
                        commit_data["files_changed"].append({
                            "filename": file.filename,
                            "additions": file.additions,
                            "deletions": file.deletions
                        })
                        file_changes[file.filename] += 1
            except Exception as e:
                print(f" Could not fetch file details for commit {commit.sha[:8]}: {e}")
                commit_data["files_changed"] = []

            result.append(commit_data)

    commit_count = sum(1 for _ in commits)
    print(f" Collected {commit_count} commits in the last 30 days.")
    print(f" Found {len(pull_requests)} pull requests with review data")
    
    state["commits"] = result
    state["pull_requests"] = pull_requests  # Add pull_requests to state
    state["file_hotspots"] = dict(sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return state

def classify_commit_type(message):
    """Helper function to classify commit types"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['fix', 'bug', 'patch', 'hotfix']):
        return 'bugfix'
    elif any(word in message_lower for word in ['feat', 'feature', 'add', 'implement']):
        return 'feature'
    elif any(word in message_lower for word in ['refactor', 'cleanup', 'improve', 'optimize']):
        return 'refactor'
    elif any(word in message_lower for word in ['test', 'spec', 'unit test']):
        return 'test'
    elif any(word in message_lower for word in ['doc', 'readme', 'comment']):
        return 'documentation'
    elif any(word in message_lower for word in ['merge', 'pull request']):
        return 'merge'
    else:
        return 'other'