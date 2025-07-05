import os, requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_API = 'https://api.github.com'

def fetch_commits(per_page=10):
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/commits"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"per_page": per_page}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"GitHub API error (commits): {e}")
        return []

def fetch_commit_details(sha):
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/commits/{sha}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"GitHub API error (commit details): {e}")
        return None

def fetch_prs(state="all", per_page=10):
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"state": state, "per_page": per_page}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"GitHub API error (prs): {e}")
        return []

def fetch_merged_prs_last_week():
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"state": "closed", "per_page": 100}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        prs = response.json()
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        merged_prs = [pr for pr in prs if pr.get('merged_at') and datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ") > one_week_ago]
        return merged_prs
    except requests.RequestException as e:
        print(f"GitHub API error (merged PRs last week): {e}")
        return []

def fetch_review_latency(prs):
    # Average time from PR creation to merge (in hours)
    times = []
    for pr in prs:
        if pr.get('merged_at'):
            created = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            merged = datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
            times.append((merged - created).total_seconds() / 3600)
    return sum(times) / len(times) if times else 0

def fetch_cycle_time(prs):
    # Average time from first commit to merge (in hours)
    times = []
    for pr in prs:
        if pr.get('merged_at'):
            commits_url = pr['commits_url']
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            try:
                resp = requests.get(commits_url, headers=headers, timeout=10)
                resp.raise_for_status()
                commits = resp.json()
                if commits:
                    first_commit_time = datetime.strptime(commits[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
                    merged = datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
                    times.append((merged - first_commit_time).total_seconds() / 3600)
            except Exception:
                continue
    return sum(times) / len(times) if times else 0

def fetch_ci_failures():
    # Count failed workflow runs in the last week
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/actions/runs"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"per_page": 100}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        runs = response.json().get('workflow_runs', [])
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        failures = [run for run in runs if run['conclusion'] == 'failure' and datetime.strptime(run['created_at'], "%Y-%m-%dT%H:%M:%SZ") > one_week_ago]
        return len(failures)
    except Exception as e:
        print(f"GitHub API error (ci failures): {e}")
        return 0

def fetch_prs_with_reviews(state="all", per_page=10):
    """Fetch PRs with their review data for influence map analysis."""
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"state": state, "per_page": per_page}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        prs = response.json()
        
        # Fetch reviews for each PR
        for pr in prs:
            reviews_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls/{pr['number']}/reviews"
            try:
                reviews_response = requests.get(reviews_url, headers=headers, timeout=10)
                reviews_response.raise_for_status()
                pr['reviews'] = reviews_response.json()
            except Exception as e:
                print(f"Error fetching reviews for PR {pr['number']}: {e}")
                pr['reviews'] = []
        
        return prs
    except requests.RequestException as e:
        print(f"GitHub API error (prs with reviews): {e}")
        return []

