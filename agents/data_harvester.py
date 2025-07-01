# data_harvester.py
from github import Github
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def data_harvester_node(state):
    print("\n🔍 [DataHarvesterAgent] Fetching GitHub data...")

    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    since = datetime.utcnow() - timedelta(days=30)

    g = Github(token)
    repo = g.get_repo(repo_name)
    commits = repo.get_commits(since=since)

    result = []
    for commit in commits:
        if commit.author:
            result.append({
                "author": commit.author.login,
                "message": commit.commit.message,
                "date": str(commit.commit.author.date),
                "additions": commit.stats.additions,
                "deletions": commit.stats.deletions,
                "total": commit.stats.total,
            })

    print(f"✅ Collected {len(result)} commits.")
    state["commit_data"] = result
    return state
