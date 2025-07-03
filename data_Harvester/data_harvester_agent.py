# data_harvester/agent.py
from data_Harvester.fetcher import data_harvester
from data_Harvester.json_storage import load_json_if_exists
from langchain_core.tools import tool
from data_Harvester.utils import is_file_stale
@tool
def data_harvester_agent(repo_owner: str, repo_name: str) -> dict:
    """
    Smart agent that fetches fresh GitHub data if cache is old or missing.
    """
    
    commit_path = "data/commits.json"
    pr_path = "data/pull_request.json"

    commits_stale = is_file_stale(commit_path, max_age_minutes=10)
    pr_stale = is_file_stale(pr_path, max_age_minutes=10)

    if commits_stale or pr_stale:
        print("🔁 Cache expired — fetching fresh data...")
        harvester = data_harvester(repo_name=repo_owner, repo=repo_name)
        harvester.fetch_commit_data()
        harvester.fetch_number_of_pull_request()

    commits = load_json_if_exists(commit_path)
    pull_requests = load_json_if_exists(pr_path)

    return {
        "commits": commits,
        "pull_requests": pull_requests
    }