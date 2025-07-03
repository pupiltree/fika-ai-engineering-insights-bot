"""GitHub API client for fetching repository data."""
import requests
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from ..config import settings, logger
from .models import GitHubEvent, EventType


class GitHubClient:
    """Client for interacting with GitHub REST API."""
    
    def __init__(self, token: str = None):
        self.token = token or settings.github_token
        self.base_url = settings.github_api_base
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Engineering-Productivity-MVP/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API with rate limiting."""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            response = self.session.get(url, params=params, timeout=settings.timeout_seconds)
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - int(time.time()), 60)
                logger.warning(f"Rate limited. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                return self._make_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise
    
    def get_commits(
        self, 
        owner: str, 
        repo: str, 
        since: datetime = None, 
        until: datetime = None,
        author: str = None,
        page: int = 1,
        per_page: int = 100
    ) -> List[GitHubEvent]:
        """Fetch commit events from GitHub API."""
        endpoint = f"/repos/{owner}/{repo}/commits"
        
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if since:
            params['since'] = since.isoformat()
        if until:
            params['until'] = until.isoformat()
        if author:
            params['author'] = author
            
        logger.info(f"Fetching commits for {owner}/{repo} (page {page})")
        
        try:
            commits_data = self._make_request(endpoint, params)
            events = []
            
            for commit_data in commits_data:
                # Get detailed commit info for diff stats
                commit_sha = commit_data['sha']
                commit_detail = self._make_request(f"/repos/{owner}/{repo}/commits/{commit_sha}")
                
                event = GitHubEvent(
                    id=f"commit_{commit_sha}",
                    repo_name=f"{owner}/{repo}",
                    event_type=EventType.COMMIT,
                    author=commit_data['commit']['author']['name'],
                    timestamp=datetime.fromisoformat(
                        commit_data['commit']['author']['date'].replace('Z', '+00:00')
                    ),
                    raw_data=commit_detail,
                    additions=commit_detail['stats'].get('additions', 0),
                    deletions=commit_detail['stats'].get('deletions', 0),
                    changed_files=len(commit_detail.get('files', [])),
                    commit_sha=commit_sha
                )
                events.append(event)
                
            logger.info(f"Retrieved {len(events)} commit events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching commits: {e}")
            return []
    
    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = 'all',  # open, closed, all
        since: datetime = None,
        page: int = 1,
        per_page: int = 100
    ) -> List[GitHubEvent]:
        """Fetch pull request events from GitHub API."""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        
        params = {
            'state': state,
            'page': page,
            'per_page': per_page,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        logger.info(f"Fetching PRs for {owner}/{repo} (page {page})")
        
        try:
            prs_data = self._make_request(endpoint, params)
            events = []
            
            for pr_data in prs_data:
                # Filter by date if specified
                updated_at = datetime.fromisoformat(
                    pr_data['updated_at'].replace('Z', '+00:00')
                )
                
                if since and updated_at < since:
                    continue
                
                # Get PR file changes for diff stats
                pr_number = pr_data['number']
                files_data = self._make_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
                
                # Calculate total additions/deletions
                total_additions = sum(file.get('additions', 0) for file in files_data)
                total_deletions = sum(file.get('deletions', 0) for file in files_data)
                
                event = GitHubEvent(
                    id=f"pr_{pr_number}",
                    repo_name=f"{owner}/{repo}",
                    event_type=EventType.PULL_REQUEST,
                    author=pr_data['user']['login'],
                    timestamp=updated_at,
                    raw_data={**pr_data, 'files': files_data},
                    additions=total_additions,
                    deletions=total_deletions,
                    changed_files=len(files_data),
                    pr_number=pr_number
                )
                events.append(event)
                
            logger.info(f"Retrieved {len(events)} PR events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching pull requests: {e}")
            return []
    
    def get_pull_request_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[GitHubEvent]:
        """Fetch PR review events for calculating review latency."""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        try:
            reviews_data = self._make_request(endpoint)
            events = []
            
            for review_data in reviews_data:
                if review_data['state'] in ['APPROVED', 'CHANGES_REQUESTED']:
                    event = GitHubEvent(
                        id=f"review_{review_data['id']}",
                        repo_name=f"{owner}/{repo}",
                        event_type=EventType.PULL_REQUEST_REVIEW,
                        author=review_data['user']['login'],
                        timestamp=datetime.fromisoformat(
                            review_data['submitted_at'].replace('Z', '+00:00')
                        ),
                        raw_data=review_data,
                        pr_number=pr_number
                    )
                    events.append(event)
                    
            return events
            
        except Exception as e:
            logger.error(f"Error fetching PR reviews: {e}")
            return []
    
    def get_repository_events(
        self,
        owner: str = None,
        repo: str = None,
        since: datetime = None,
        until: datetime = None,
        include_prs: bool = True,
        include_commits: bool = True
    ) -> List[GitHubEvent]:
        """Fetch all repository events for the specified time period."""
        owner = owner or settings.default_repo_owner
        repo = repo or settings.default_repo_name
        since = since or (datetime.now() - timedelta(days=settings.default_lookback_days))
        
        logger.info(f"Fetching repository events for {owner}/{repo} since {since}")
        
        all_events = []
        
        # Fetch commits
        if include_commits:
            commits = self.get_commits(owner, repo, since, until)
            all_events.extend(commits)
        
        # Fetch pull requests
        if include_prs:
            prs = self.get_pull_requests(owner, repo, since=since)
            all_events.extend(prs)
            
            # Fetch reviews for each PR
            for pr_event in prs:
                if pr_event.pr_number:
                    reviews = self.get_pull_request_reviews(owner, repo, pr_event.pr_number)
                    all_events.extend(reviews)
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"Retrieved {len(all_events)} total events")
        return all_events
    
    def test_connection(self) -> bool:
        """Test GitHub API connection and authentication."""
        try:
            response = self._make_request('/user')
            logger.info(f"GitHub API connection successful. User: {response.get('login')}")
            return True
        except Exception as e:
            logger.error(f"GitHub API connection failed: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        try:
            response = self._make_request('/rate_limit')
            return response['rate']
        except Exception as e:
            logger.error(f"Error fetching rate limit: {e}")
            return {}


# Global GitHub client instance
github_client = GitHubClient()