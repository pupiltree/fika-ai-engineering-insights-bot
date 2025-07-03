# agents/data_harvester.py

import requests, os, json
from typing import Dict, Tuple
from datetime import datetime

class DataHarvesterAgent:
    def __init__(self):
        self.name = "DataHarvester"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPO")
        self.headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
        self.seed_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_data.json")
        print(f"📡 {self.name} initialized")

    def run(self, state: Dict) -> Dict:
        repo = self.repo or state.get("repo")
        use_seed = state.get("use_seed", True)

        if use_seed:
            print("📦 Loading from seed data...")
            with open(self.seed_data_path, "r") as f:
                seed = json.load(f)
            commits = seed.get("commits", [])
            prs = seed.get("prs", [])
        else:
            commits, prs = self.fetch_github_data(repo)
            if not commits and not prs:
                print("⚠️ No data from GitHub, falling back to seed data...")
                with open(self.seed_data_path, "r") as f:
                    seed = json.load(f)
                commits = seed.get("commits", [])
                prs = seed.get("prs", [])

        return {
            **state,
            "repo": repo,
            "commits": commits,
            "prs": prs,
        }

    def fetch_github_data(self, repo: str) -> Tuple[list, list]:
        commits = self.fetch_commits(repo)
        prs = self.fetch_prs(repo)
        return commits, prs

    def fetch_commits(self, repo: str, limit: int = 30) -> list:
        print(f"📥 Fetching commits for {repo}")
        url = f"https://api.github.com/repos/{repo}/commits?per_page={limit}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"❌ Commit fetch failed: {response.status_code}")
            return []

        commits = []
        for c in response.json():
            commit_data = c.get("commit", {})
            author_info = commit_data.get("author", {})
            commit = {
                "sha": c["sha"],
                "author": author_info.get("name", "unknown"),
                "date": author_info.get("date", ""),
                "message": commit_data.get("message", ""),
                "additions": 0,
                "deletions": 0,
                "files_changed": 0,
                "after_hours": self.is_after_hours(author_info.get("date")),
                "is_risky": False
            }
            commits.append(commit)
        return commits

    def fetch_prs(self, repo: str, limit: int = 20) -> list:
        print(f"🔍 Fetching PRs for {repo}")
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page={limit}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"❌ PR fetch failed: {response.status_code}")
            return []

        prs = []
        for pr in response.json():
            if not pr.get("merged_at"):
                continue
            latency = self.calculate_latency(pr.get("created_at"), pr.get("merged_at"))
            prs.append({
                "pr_id": f"PR{pr['number']}",
                "author": pr["user"]["login"],
                "created_at": pr["created_at"],
                "merged_at": pr["merged_at"],
                "review_latency_hrs": latency,
                "ci_status": "unknown",
                "commits": []
            })
        return prs

    def calculate_latency(self, created: str, merged: str) -> float:
        try:
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            created_dt = datetime.strptime(created, fmt)
            merged_dt = datetime.strptime(merged, fmt)
            return round((merged_dt - created_dt).total_seconds() / 3600, 2)
        except Exception as e:
            print(f"⚠️ Latency calculation error: {e}")
            return 0.0

    def is_after_hours(self, iso_date: str) -> bool:
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.hour < 9 or dt.hour > 19
        except:
            return False
