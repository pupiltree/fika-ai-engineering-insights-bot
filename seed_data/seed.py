#!/usr/bin/env python3

"""
Seed script for PowerBiz Developer Analytics

This script generates fake GitHub data for testing purposes.
"""

import os
import sys
import random
import datetime
import logging
from pathlib import Path
import json

# Add the parent directory to the path so we can import the package
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from powerbiz.database.db import init_db, get_session
from powerbiz.database.models import (
    Developer, Team, Repository, Commit, PullRequest, Review,
    CIBuild, Deployment, Incident
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data
DEVELOPERS = [
    {"github_username": "alice", "name": "Alice Johnson", "email": "alice@example.com"},
    {"github_username": "bob", "name": "Bob Smith", "email": "bob@example.com"},
    {"github_username": "carol", "name": "Carol Zhang", "email": "carol@example.com"},
    {"github_username": "dave", "name": "Dave Brown", "email": "dave@example.com"},
    {"github_username": "eve", "name": "Eve Williams", "email": "eve@example.com"},
    {"github_username": "frank", "name": "Frank Lee", "email": "frank@example.com"},
    {"github_username": "grace", "name": "Grace Kim", "email": "grace@example.com"},
]

TEAMS = [
    {"name": "Frontend", "description": "Frontend development team"},
    {"name": "Backend", "description": "Backend development team"},
    {"name": "DevOps", "description": "DevOps and infrastructure team"},
]

REPOSITORIES = [
    {
        "github_id": 12345678,
        "name": "web-app",
        "full_name": "acme/web-app",
        "description": "ACME Web Application"
    },
    {
        "github_id": 23456789,
        "name": "api-service",
        "full_name": "acme/api-service",
        "description": "ACME API Service"
    },
    {
        "github_id": 34567890,
        "name": "infrastructure",
        "full_name": "acme/infrastructure",
        "description": "ACME Infrastructure Configuration"
    },
]

# Commit messages
COMMIT_MESSAGES = [
    "Add new feature",
    "Fix bug in login flow",
    "Update dependencies",
    "Refactor user authentication",
    "Implement search functionality",
    "Fix typos in documentation",
    "Optimize database queries",
    "Add unit tests",
    "Fix failing tests",
    "Update README",
    "Add error handling",
    "Implement caching layer",
    "Fix security vulnerability",
    "Improve UI/UX",
    "Add logging",
    "Refactor code for better readability",
    "Fix edge case in payment processing",
    "Add new API endpoint",
    "Update API documentation",
    "Fix CSS issues",
]

# PR titles
PR_TITLES = [
    "Add user authentication",
    "Fix login issues",
    "Implement search feature",
    "Update dependencies",
    "Add documentation",
    "Fix failing tests",
    "Optimize performance",
    "Implement caching",
    "Refactor user service",
    "Add logging",
    "Fix security issues",
    "Add API endpoints",
    "Update UI components",
    "Fix edge cases",
    "Add unit tests",
    "Update README",
    "Fix typos",
    "Improve error handling",
    "Update build pipeline",
    "Fix CSS issues",
]

def create_seed_data():
    """Create seed data in the database."""
    logger.info("Creating seed data...")
    
    # Initialize the database
    init_db()
    
    session = get_session()
    
    try:
        # Add teams
        teams = []
        for team_data in TEAMS:
            team = Team(**team_data)
            session.add(team)
            teams.append(team)
        
        session.flush()
        
        # Add developers
        developers = []
        for idx, dev_data in enumerate(DEVELOPERS):
            # Assign to a team
            team_id = teams[idx % len(teams)].id
            developer = Developer(team_id=team_id, **dev_data)
            session.add(developer)
            developers.append(developer)
        
        session.flush()
        
        # Add repositories
        repositories = []
        for repo_data in REPOSITORIES:
            repository = Repository(**repo_data)
            session.add(repository)
            repositories.append(repository)
        
        session.flush()
        
        # Generate commits and PRs for the past 30 days
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.datetime.timedelta(days=30)
        
        # Helper function to get a random date in the range
        def random_date(start, end):
            return start + datetime.timedelta(
                seconds=random.randint(0, int((end - start).total_seconds()))
            )
        
        # Create commits
        commits = []
        for repo in repositories:
            # Create 100-300 commits per repository
            num_commits = random.randint(100, 300)
            for _ in range(num_commits):
                # Pick a random developer
                developer = random.choice(developers)
                
                # Generate commit date
                commit_date = random_date(start_date, end_date)
                
                # Generate commit stats
                additions = random.randint(5, 500)
                deletions = random.randint(1, additions)
                changed_files = random.randint(1, 10)
                
                # Create commit
                commit = Commit(
                    sha=f"{random.getrandbits(160):040x}",  # Random SHA-1 hash
                    message=random.choice(COMMIT_MESSAGES),
                    developer_id=developer.id,
                    repository_id=repo.id,
                    additions=additions,
                    deletions=deletions,
                    changed_files=changed_files,
                    commit_date=commit_date
                )
                session.add(commit)
                commits.append(commit)
        
        session.flush()
        
        # Create PRs
        pull_requests = []
        for repo in repositories:
            # Create 30-50 PRs per repository
            num_prs = random.randint(30, 50)
            for _ in range(num_prs):
                # Pick a random developer
                author = random.choice(developers)
                
                # Generate PR dates
                created_at = random_date(start_date, end_date)
                
                # Determine if PR is merged/closed
                state = random.choice(["open", "closed", "merged"])
                is_merged = (state == "merged")
                
                updated_at = None
                merged_at = None
                closed_at = None
                lead_time_minutes = None
                
                if state in ["closed", "merged"]:
                    # PR is closed or merged
                    closed_delay = datetime.timedelta(hours=random.randint(1, 72))
                    closed_at = created_at + closed_delay
                    updated_at = closed_at
                    
                    if is_merged:
                        merged_at = closed_at
                        lead_time_minutes = closed_delay.total_seconds() / 60
                
                # Generate PR stats
                additions = random.randint(50, 1000)
                deletions = random.randint(10, additions)
                changed_files = random.randint(1, 20)
                
                # Create PR
                pr = PullRequest(
                    github_id=random.randint(100000, 999999),
                    title=random.choice(PR_TITLES),
                    description="This is a sample PR description.",
                    author_id=author.id,
                    repository_id=repo.id,
                    additions=additions,
                    deletions=deletions,
                    changed_files=changed_files,
                    state=state,
                    is_merged=is_merged,
                    created_at=created_at,
                    updated_at=updated_at,
                    merged_at=merged_at,
                    closed_at=closed_at,
                    lead_time_minutes=lead_time_minutes
                )
                session.add(pr)
                session.flush()  # To get the PR ID
                
                # Add reviews (if not open)
                if state in ["closed", "merged"]:
                    # Add 1-5 reviews
                    num_reviews = random.randint(1, 5)
                    for _ in range(num_reviews):
                        # Pick a random reviewer (different from the author)
                        reviewers = [d for d in developers if d.id != author.id]
                        reviewer = random.choice(reviewers)
                        
                        # Generate review date (between PR creation and close)
                        review_date = random_date(created_at, closed_at)
                        
                        # Create review
                        review = Review(
                            github_id=random.randint(1000000, 9999999),
                            pull_request_id=pr.id,
                            reviewer_id=reviewer.id,
                            state=random.choice(["APPROVED", "CHANGES_REQUESTED", "COMMENTED"]),
                            submitted_at=review_date
                        )
                        session.add(review)
                
                # Update review count
                review_count = session.query(Review).filter_by(pull_request_id=pr.id).count()
                pr.review_count = review_count
                
                pull_requests.append(pr)
        
        session.flush()
        
        # Create CI builds
        ci_builds = []
        for repo in repositories:
            # Create builds for each PR
            repo_prs = [pr for pr in pull_requests if pr.repository_id == repo.id]
            for pr in repo_prs:
                # 1-3 builds per PR
                num_builds = random.randint(1, 3)
                for _ in range(num_builds):
                    # Generate build timing
                    started_at = random_date(pr.created_at, pr.closed_at or end_date)
                    completed_at = started_at + datetime.timedelta(minutes=random.randint(5, 30))
                    duration_seconds = (completed_at - started_at).total_seconds()
                    
                    # Create build
                    build = CIBuild(
                        external_id=f"build-{random.randint(10000, 99999)}",
                        pull_request_id=pr.id,
                        commit_sha=f"{random.getrandbits(160):040x}",
                        status=random.choices(
                            ["success", "failure", "pending"],
                            weights=[0.8, 0.15, 0.05]
                        )[0],
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_seconds=duration_seconds
                    )
                    session.add(build)
                    ci_builds.append(build)
        
        session.flush()
        
        # Create deployments
        deployments = []
        for repo in repositories:
            # Create 10-20 deployments per repository
            num_deployments = random.randint(10, 20)
            for _ in range(num_deployments):
                # Generate deployment date
                deployed_at = random_date(start_date, end_date)
                
                # Create deployment
                deployment = Deployment(
                    external_id=f"deploy-{random.randint(10000, 99999)}",
                    repository_id=repo.id,
                    commit_sha=f"{random.getrandbits(160):040x}",
                    status="success",
                    environment=random.choice(["production", "staging"]),
                    deployed_at=deployed_at
                )
                session.add(deployment)
                deployments.append(deployment)
        
        session.flush()
        
        # Create incidents
        incidents = []
        for repo in repositories:
            # Create 3-8 incidents per repository
            num_incidents = random.randint(3, 8)
            for _ in range(num_incidents):
                # Generate incident dates
                detected_at = random_date(start_date, end_date)
                
                # Determine if resolved
                is_resolved = random.random() > 0.2  # 80% chance of being resolved
                
                resolved_at = None
                resolution_time_minutes = None
                
                if is_resolved:
                    # Incident is resolved
                    resolution_delay = datetime.timedelta(hours=random.randint(1, 24))
                    resolved_at = detected_at + resolution_delay
                    resolution_time_minutes = resolution_delay.total_seconds() / 60
                
                # Create incident
                incident = Incident(
                    title=f"Incident {random.randint(1000, 9999)}",
                    description="This is a sample incident description.",
                    repository_id=repo.id,
                    deployment_id=random.choice(deployments).id if deployments else None,
                    detected_at=detected_at,
                    resolved_at=resolved_at,
                    resolution_time_minutes=resolution_time_minutes,
                    severity=random.choice(["critical", "high", "medium", "low"])
                )
                session.add(incident)
                incidents.append(incident)
        
        # Commit all changes
        session.commit()
        
        # Log summary
        logger.info(f"Created {len(teams)} teams")
        logger.info(f"Created {len(developers)} developers")
        logger.info(f"Created {len(repositories)} repositories")
        logger.info(f"Created {len(commits)} commits")
        logger.info(f"Created {len(pull_requests)} pull requests")
        logger.info(f"Created {len(ci_builds)} CI builds")
        logger.info(f"Created {len(deployments)} deployments")
        logger.info(f"Created {len(incidents)} incidents")
        
        logger.info("Seed data created successfully!")
    
    except Exception as e:
        logger.error(f"Error creating seed data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    create_seed_data()

def create_sample_data():
    """Alias for create_seed_data() for compatibility."""
    return create_seed_data()

def main():
    """Main entry point."""
    create_seed_data()
