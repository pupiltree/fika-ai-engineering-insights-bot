import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def fetch_commits(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = httpx.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_commit_details(owner, repo, sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    response = httpx.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()
