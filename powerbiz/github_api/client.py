"""
GitHub API client for retrieving repository data
"""

import os
import logging
import aiohttp
import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for GitHub API to fetch commits, PRs, and other data."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client.
        
        Args:
            token: GitHub API token. If not provided, will try to get it from environment variable.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            logger.warning("GitHub token not provided. API rate limits will be restricted.")
        
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

    async def get_commits(
        self, 
        owner: str, 
        repo: str, 
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """Get commits for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            since: Only show commits after this date
            until: Only show commits before this date
            per_page: Results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of commits
        """
        params = {"per_page": per_page}
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        
        all_commits = []
        page = 1
        
        async with aiohttp.ClientSession() as session:
            while page <= max_pages:
                params["page"] = page
                async with session.get(url, headers=self.headers, params=params) as response:
                    response.raise_for_status()
                    commits = await response.json()
                    
                    if not commits:
                        break
                        
                    all_commits.extend(commits)
                    page += 1
                    
                    # Check if we've reached the end
                    if len(commits) < per_page:
                        break
        
        return all_commits

    async def get_commit_detail(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Get detailed information for a specific commit.
        
        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA
            
        Returns:
            Detailed commit information including stats
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits/{sha}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",  # "open", "closed", "all"
        sort: str = "created",  # "created", "updated", "popularity", "long-running"
        direction: str = "desc",  # "asc", "desc"
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """Get pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            sort: Sort field
            direction: Sort direction
            per_page: Results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of pull requests
        """
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": per_page
        }
        
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls"
        
        all_prs = []
        page = 1
        
        async with aiohttp.ClientSession() as session:
            while page <= max_pages:
                params["page"] = page
                async with session.get(url, headers=self.headers, params=params) as response:
                    response.raise_for_status()
                    prs = await response.json()
                    
                    if not prs:
                        break
                        
                    all_prs.extend(prs)
                    page += 1
                    
                    # Check if we've reached the end
                    if len(prs) < per_page:
                        break
        
        return all_prs

    async def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of files changed in the PR with additions, deletions, etc.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

    async def get_pull_request_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get reviews for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of reviews
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

    async def get_workflow_runs(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        per_page: int = 100,
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """Get GitHub Actions workflow runs.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Filter by branch name
            per_page: Results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of workflow runs
        """
        params = {"per_page": per_page}
        if branch:
            params["branch"] = branch
        
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/actions/runs"
        
        all_runs = []
        page = 1
        
        async with aiohttp.ClientSession() as session:
            while page <= max_pages:
                params["page"] = page
                async with session.get(url, headers=self.headers, params=params) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    runs = response_data.get("workflow_runs", [])
                    
                    if not runs:
                        break
                        
                    all_runs.extend(runs)
                    page += 1
                    
                    # Check if we've reached the end
                    if len(runs) < per_page:
                        break
        
        return all_runs

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get GitHub user information.
        
        Args:
            username: GitHub username
            
        Returns:
            User information
        """
        url = f"{self.BASE_URL}/users/{username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
