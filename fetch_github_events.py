import os, requests
from dotenv import load_dotenv
from state_schema import MyState

load_dotenv()
GITHUB_TOKEN = "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"





def data_harvester_agent(state: MyState) -> MyState:
    print("🛰️ DataHarvesterAgent: fetching real GitHub data...")
    owner, repo, per_page = "vercel", "next.js", 10

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/events"
    response = requests.get(url, headers=headers, params={"per_page": per_page})

    if response.status_code != 200:
        print("❌ Failed to fetch GitHub events:", response.status_code)
        state["events"] = []
        return state

    raw_events = response.json()
    push_events = [e for e in raw_events if e["type"] == "PushEvent"]
    simplified_events = []

    for event in push_events:
        author = event.get("actor", {}).get("login", "unknown")
        commits = event.get("payload", {}).get("commits", [])

        for commit in commits:
            sha = commit.get("sha")
            commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
            commit_resp = requests.get(commit_url, headers=headers)

            if commit_resp.status_code == 200:
                commit_data = commit_resp.json()
                stats = commit_data.get("stats", {})
                simplified_events.append({
                    "author": author,
                    "add": stats.get("additions", 0),
                    "del": stats.get("deletions", 0),
                    "files": stats.get("total", 0)
                })
            else:
                print(f"⚠️ Failed to fetch commit {sha}")

    state["events"] = simplified_events
    return state