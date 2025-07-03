"""
Data harvester for GitHub repositories
"""

import logging
import datetime
from typing import List, Dict, Any, Optional

from powerbiz.github_api.client import GitHubClient
from powerbiz.database.db import get_session
from powerbiz.database.models import (
    Developer, Repository, Commit, PullRequest, Review, CIBuild
)

logger = logging.getLogger(__name__)

class GitHubDataHarvester:
    """Harvests data from GitHub repositories and stores in database."""
    
    def __init__(self, github_client: Optional[GitHubClient] = None):
        """Initialize the data harvester.
        
        Args:
            github_client: GitHub API client. If not provided, a new one will be created.
        """
        self.github_client = github_client or GitHubClient()
    
    async def harvest_repository(self, owner: str, repo: str) -> Repository:
        """Harvest repository data and store in database.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository database object
        """
        repo_data = await self.github_client.get_repository(owner, repo)
        
        session = get_session()
        try:
            # Check if repository exists in database
            repository = session.query(Repository).filter_by(github_id=repo_data["id"]).first()
            
            if not repository:
                repository = Repository(
                    github_id=repo_data["id"],
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    description=repo_data.get("description")
                )
                session.add(repository)
            else:
                # Update existing repository
                repository.name = repo_data["name"]
                repository.full_name = repo_data["full_name"]
                repository.description = repo_data.get("description")
            
            session.commit()
            return repository
        finally:
            session.close()

    async def harvest_commits(
        self,
        owner: str,
        repo: str,
        repository_id: int,
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None
    ) -> List[Commit]:
        """Harvest commit data and store in database.
        
        Args:
            owner: Repository owner
            repo: Repository name
            repository_id: Database ID of the repository
            since: Only fetch commits after this date
            until: Only fetch commits before this date
            
        Returns:
            List of database commit objects
        """
        commits_data = await self.github_client.get_commits(
            owner, repo, since=since, until=until
        )
        
        db_commits = []
        session = get_session()
        
        try:
            for commit_summary in commits_data:
                # Skip if we already have this commit
                existing = session.query(Commit).filter_by(sha=commit_summary["sha"]).first()
                if existing:
                    db_commits.append(existing)
                    continue
                
                # Get detailed commit info
                commit_detail = await self.github_client.get_commit_detail(
                    owner, repo, commit_summary["sha"]
                )
                
                # Get or create developer
                author_data = commit_summary.get("author") or {}
                author_username = author_data.get("login")
                
                developer = None
                if author_username:
                    developer = session.query(Developer).filter_by(
                        github_username=author_username
                    ).first()
                    
                    if not developer:
                        # Fetch user details
                        try:
                            user_info = await self.github_client.get_user_info(author_username)
                            developer = Developer(
                                github_username=author_username,
                                name=user_info.get("name"),
                                email=user_info.get("email")
                            )
                            session.add(developer)
                            session.flush()  # Get developer ID
                        except Exception as e:
                            logger.error(f"Failed to get user info: {e}")
                            continue
                else:
                    # Skip commits without author info
                    logger.warning(f"Commit {commit_summary['sha']} has no author, skipping")
                    continue
                
                # Parse commit date
                commit_date = datetime.datetime.fromisoformat(
                    commit_detail["commit"]["author"]["date"].replace("Z", "+00:00")
                )
                
                # Create commit object
                commit = Commit(
                    sha=commit_summary["sha"],
                    message=commit_detail["commit"]["message"],
                    developer_id=developer.id,
                    repository_id=repository_id,
                    additions=commit_detail["stats"].get("additions", 0),
                    deletions=commit_detail["stats"].get("deletions", 0),
                    changed_files=len(commit_detail.get("files", [])),
                    commit_date=commit_date
                )
                
                session.add(commit)
                db_commits.append(commit)
            
            session.commit()
            return db_commits
        finally:
            session.close()

    async def harvest_pull_requests(
        self,
        owner: str,
        repo: str,
        repository_id: int,
        state: str = "all"
    ) -> List[PullRequest]:
        """Harvest pull request data and store in database.
        
        Args:
            owner: Repository owner
            repo: Repository name
            repository_id: Database ID of the repository
            state: PR state to fetch (open, closed, all)
            
        Returns:
            List of database PR objects
        """
        prs_data = await self.github_client.get_pull_requests(owner, repo, state=state)
        
        db_prs = []
        session = get_session()
        
        try:
            for pr_data in prs_data:
                # Skip if we already have this PR
                existing = session.query(PullRequest).filter_by(github_id=pr_data["id"]).first()
                if existing:
                    db_prs.append(existing)
                    continue
                
                # Get author (or create)
                author_username = pr_data["user"]["login"]
                author = session.query(Developer).filter_by(
                    github_username=author_username
                ).first()
                
                if not author:
                    # Fetch user details
                    try:
                        user_info = await self.github_client.get_user_info(author_username)
                        author = Developer(
                            github_username=author_username,
                            name=user_info.get("name"),
                            email=user_info.get("email")
                        )
                        session.add(author)
                        session.flush()  # Get author ID
                    except Exception as e:
                        logger.error(f"Failed to get user info: {e}")
                        continue
                
                # Get PR files for stats
                pr_files = await self.github_client.get_pull_request_files(
                    owner, repo, pr_data["number"]
                )
                
                additions = sum(file.get("additions", 0) for file in pr_files)
                deletions = sum(file.get("deletions", 0) for file in pr_files)
                
                # Parse dates
                created_at = datetime.datetime.fromisoformat(
                    pr_data["created_at"].replace("Z", "+00:00")
                )
                
                updated_at = None
                if pr_data.get("updated_at"):
                    updated_at = datetime.datetime.fromisoformat(
                        pr_data["updated_at"].replace("Z", "+00:00")
                    )
                
                merged_at = None
                if pr_data.get("merged_at"):
                    merged_at = datetime.datetime.fromisoformat(
                        pr_data["merged_at"].replace("Z", "+00:00")
                    )
                
                closed_at = None
                if pr_data.get("closed_at"):
                    closed_at = datetime.datetime.fromisoformat(
                        pr_data["closed_at"].replace("Z", "+00:00")
                    )
                
                # Calculate lead time (time from PR creation to merge)
                lead_time_minutes = None
                if merged_at and created_at:
                    lead_time_minutes = (merged_at - created_at).total_seconds() / 60
                
                # Create PR object
                pull_request = PullRequest(
                    github_id=pr_data["id"],
                    title=pr_data["title"],
                    description=pr_data.get("body"),
                    author_id=author.id,
                    repository_id=repository_id,
                    additions=additions,
                    deletions=deletions,
                    changed_files=len(pr_files),
                    state=pr_data["state"],
                    is_merged=bool(pr_data.get("merged_at")),
                    created_at=created_at,
                    updated_at=updated_at,
                    merged_at=merged_at,
                    closed_at=closed_at,
                    lead_time_minutes=lead_time_minutes
                )
                
                session.add(pull_request)
                session.flush()  # Get PR ID
                
                # Get and store PR reviews
                await self._harvest_pr_reviews(
                    owner, repo, pr_data["number"], pull_request.id, session
                )
                
                db_prs.append(pull_request)
            
            session.commit()
            return db_prs
        finally:
            session.close()

    async def _harvest_pr_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        pr_id: int,
        session
    ) -> List[Review]:
        """Harvest PR review data and store in database.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            pr_id: Database ID of the PR
            session: Database session
            
        Returns:
            List of database review objects
        """
        reviews_data = await self.github_client.get_pull_request_reviews(
            owner, repo, pr_number
        )
        
        db_reviews = []
        
        for review_data in reviews_data:
            # Skip if we already have this review
            existing = session.query(Review).filter_by(github_id=review_data["id"]).first()
            if existing:
                db_reviews.append(existing)
                continue
            
            # Get reviewer (or create)
            reviewer_username = review_data["user"]["login"]
            reviewer = session.query(Developer).filter_by(
                github_username=reviewer_username
            ).first()
            
            if not reviewer:
                # Fetch user details
                try:
                    user_info = await self.github_client.get_user_info(reviewer_username)
                    reviewer = Developer(
                        github_username=reviewer_username,
                        name=user_info.get("name"),
                        email=user_info.get("email")
                    )
                    session.add(reviewer)
                    session.flush()  # Get reviewer ID
                except Exception as e:
                    logger.error(f"Failed to get user info: {e}")
                    continue
            
            # Parse date
            submitted_at = datetime.datetime.fromisoformat(
                review_data["submitted_at"].replace("Z", "+00:00")
            )
            
            # Create review object
            review = Review(
                github_id=review_data["id"],
                pull_request_id=pr_id,
                reviewer_id=reviewer.id,
                state=review_data["state"],
                submitted_at=submitted_at
            )
            
            session.add(review)
            db_reviews.append(review)
        
        # Update review count on the PR
        pr = session.query(PullRequest).get(pr_id)
        if pr:
            pr.review_count = len(db_reviews)
        
        return db_reviews

    async def harvest_ci_builds(
        self,
        owner: str,
        repo: str,
        repository_id: int
    ) -> List[CIBuild]:
        """Harvest CI build data and store in database.
        
        Args:
            owner: Repository owner
            repo: Repository name
            repository_id: Database ID of the repository
            
        Returns:
            List of database CI build objects
        """
        workflow_runs = await self.github_client.get_workflow_runs(owner, repo)
        
        db_builds = []
        session = get_session()
        
        try:
            for run in workflow_runs:
                # Skip if we already have this build
                existing = session.query(CIBuild).filter_by(external_id=str(run["id"])).first()
                if existing:
                    db_builds.append(existing)
                    continue
                
                # Find associated PR if any
                pr = None
                if run.get("pull_requests"):
                    pr_number = run["pull_requests"][0]["number"]
                    pr = session.query(PullRequest).filter_by(
                        github_id=pr_number
                    ).first()
                
                # Parse dates
                started_at = datetime.datetime.fromisoformat(
                    run["created_at"].replace("Z", "+00:00")
                )
                
                completed_at = None
                if run.get("updated_at"):
                    completed_at = datetime.datetime.fromisoformat(
                        run["updated_at"].replace("Z", "+00:00")
                    )
                
                # Calculate duration
                duration_seconds = None
                if completed_at and started_at:
                    duration_seconds = (completed_at - started_at).total_seconds()
                
                # Create build object
                build = CIBuild(
                    external_id=str(run["id"]),
                    pull_request_id=pr.id if pr else None,
                    commit_sha=run["head_sha"],
                    status=run["conclusion"] or run["status"],
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_seconds=duration_seconds
                )
                
                session.add(build)
                db_builds.append(build)
            
            session.commit()
            return db_builds
        finally:
            session.close()
