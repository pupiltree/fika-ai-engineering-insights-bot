import requests

def fetch_push_event_commits(owner, repo, token, per_page=5):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/events"
    response = requests.get(url, headers=headers, params={"per_page": per_page})

    results = []

    if response.status_code == 200:
        events = response.json()
        push_events = [e for e in events if e["type"] == "PushEvent"]

        for event in push_events:
            author = event["actor"]["login"]
            for commit in event["payload"]["commits"]:
                sha = commit["sha"]
                commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                commit_resp = requests.get(commit_url, headers=headers)

                if commit_resp.status_code == 200:
                    commit_data = commit_resp.json()
                    results.append({
                        "author": author,
                        "add": commit_data["stats"]["additions"],
                        "del": commit_data["stats"]["deletions"],
                        "files": commit_data["stats"]["total"]
                    })
    return results
