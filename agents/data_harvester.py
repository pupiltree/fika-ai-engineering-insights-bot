import requests

def fetch_github_events(repo, token):
    headers = {'Authorization': f'token {token}'}
    events = requests.get(f'https://api.github.com/repos/{repo}/events', headers=headers).json()
    # Parse commits, PRs, etc.
    return events
