#!/usr/bin/env python3
"""Seed database with sample GitHub events for demo purposes."""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.data.database import db
from src.data.models import GitHubEvent, EventType
from src.config import settings, logger


def create_sample_events() -> List[GitHubEvent]:
    """Create realistic sample GitHub events for demo."""
    
    # Base time - last week
    base_time = datetime.now() - timedelta(days=7)
    repo_name = f"{settings.default_repo_owner}/{settings.default_repo_name}"
    
    events = []
    
    # Sample developers with different activity patterns
    developers = [
        {"name": "alice.smith", "productivity": "high", "style": "frequent_small"},
        {"name": "bob.jones", "productivity": "medium", "style": "moderate"},  
        {"name": "charlie.wang", "productivity": "high", "style": "large_commits"},
        {"name": "diana.kim", "productivity": "low", "style": "infrequent"},
        {"name": "eve.garcia", "productivity": "medium", "style": "reviewer"}
    ]
    
    commit_id = 1000
    pr_id = 100
    
    # Generate commits for each developer
    for dev in developers:
        name = dev["name"]
        productivity = dev["productivity"]
        style = dev["style"]
        
        # Determine commit frequency
        if productivity == "high":
            commit_count = 15 if style == "frequent_small" else 8
        elif productivity == "medium":
            commit_count = 6
        else:
            commit_count = 2
        
        # Generate commits
        for i in range(commit_count):
            commit_time = base_time + timedelta(
                days=i * (7 / commit_count),
                hours=9 + (i * 2) % 8,  # Spread across work hours
                minutes=(i * 23) % 60
            )
            
            # Determine commit size based on style
            if style == "frequent_small":
                additions = 20 + (i * 15) % 50
                deletions = 5 + (i * 8) % 20
                files = 1 + i % 3
            elif style == "large_commits":
                additions = 150 + (i * 100) % 300
                deletions = 50 + (i * 30) % 100
                files = 8 + i % 5
            else:  # moderate or infrequent
                additions = 60 + (i * 40) % 100
                deletions = 20 + (i * 15) % 40
                files = 3 + i % 4
            
            # Create realistic commit messages
            commit_messages = [
                f"Add feature validation for user input",
                f"Fix bug in authentication flow", 
                f"Update documentation for API endpoints",
                f"Refactor database connection handling",
                f"Implement caching for performance improvement",
                f"Add unit tests for core functionality",
                f"Update dependencies to latest versions",
                f"Fix memory leak in background process",
                f"Add error handling for edge cases",
                f"Optimize query performance"
            ]
            
            message = commit_messages[i % len(commit_messages)]
            commit_sha = f"abc{commit_id:04d}ef"
            
            event = GitHubEvent(
                id=f"commit_{commit_sha}",
                repo_name=repo_name,
                event_type=EventType.COMMIT,
                author=name,
                timestamp=commit_time,
                raw_data={
                    "sha": commit_sha,
                    "commit": {
                        "author": {"name": name, "date": commit_time.isoformat()},
                        "message": message
                    },
                    "stats": {
                        "additions": additions,
                        "deletions": deletions,
                        "total": additions + deletions
                    },
                    "files": [{"filename": f"src/module{j}.py"} for j in range(files)]
                },
                additions=additions,
                deletions=deletions,
                changed_files=files,
                commit_sha=commit_sha
            )
            
            events.append(event)
            commit_id += 1
    
    # Generate some pull requests
    pr_authors = ["alice.smith", "bob.jones", "charlie.wang"]
    pr_titles = [
        "Add user authentication system",
        "Implement data validation layer", 
        "Fix performance issues in search",
        "Add comprehensive error handling",
        "Update API documentation"
    ]
    
    for i, author in enumerate(pr_authors):
        if i < len(pr_titles):
            pr_time = base_time + timedelta(days=2 + i, hours=14)
            
            event = GitHubEvent(
                id=f"pr_{pr_id}",
                repo_name=repo_name,
                event_type=EventType.PULL_REQUEST,
                author=author,
                timestamp=pr_time,
                raw_data={
                    "number": pr_id,
                    "title": pr_titles[i],
                    "state": "closed",
                    "merged_at": (pr_time + timedelta(hours=8)).isoformat(),
                    "user": {"login": author},
                    "files": [
                        {"filename": "src/auth.py", "additions": 150, "deletions": 20},
                        {"filename": "tests/test_auth.py", "additions": 80, "deletions": 5}
                    ]
                },
                additions=230,
                deletions=25,
                changed_files=2,
                pr_number=pr_id
            )
            
            events.append(event)
            pr_id += 1
    
    # Generate some PR reviews
    reviewers = ["eve.garcia", "diana.kim", "alice.smith"]
    for i, reviewer in enumerate(reviewers):
        if i < 3:  # Review first 3 PRs
            review_time = base_time + timedelta(days=2 + i, hours=16)
            
            event = GitHubEvent(
                id=f"review_{1000 + i}",
                repo_name=repo_name,
                event_type=EventType.PULL_REQUEST_REVIEW,
                author=reviewer,
                timestamp=review_time,
                raw_data={
                    "id": 1000 + i,
                    "state": "APPROVED" if i % 2 == 0 else "CHANGES_REQUESTED",
                    "submitted_at": review_time.isoformat(),
                    "user": {"login": reviewer}
                },
                pr_number=100 + i
            )
            
            events.append(event)
    
    logger.info(f"Generated {len(events)} sample events")
    return events


def seed_database():
    """Seed the database with sample data."""
    logger.info("Seeding database with sample GitHub events...")
    
    try:
        # Create sample events
        events = create_sample_events()
        
        # Insert events into database
        success_count = 0
        for event in events:
            if db.insert_github_event(event):
                success_count += 1
        
        logger.info(f"✅ Successfully inserted {success_count}/{len(events)} events")
        
        # Show database stats
        stats = db.get_stats()
        logger.info(f"📊 Database stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        return False


def create_sample_json():
    """Create sample JSON file for reference."""
    events = create_sample_events()
    
    # Convert to JSON serializable format
    events_data = []
    for event in events:
        event_dict = event.dict()
        event_dict["timestamp"] = event_dict["timestamp"].isoformat()
        events_data.append(event_dict)
    
    # Ensure seed directory exists
    seed_dir = Path("data/seed")
    seed_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON file
    json_path = seed_dir / "sample_github_events.json"
    with open(json_path, "w") as f:
        json.dump(events_data, f, indent=2)
    
    logger.info(f"📄 Sample JSON saved to {json_path}")


def main():
    """Main seeding function."""
    print("🌱 Engineering Productivity MVP - Database Seeding")
    print("=" * 50)
    
    # Create sample JSON file
    create_sample_json()
    
    # Seed database
    success = seed_database()
    
    if success:
        print("\n✅ Database seeded successfully!")
        print("\nSample data includes:")
        print("• 5 developers with different productivity patterns")
        print("• ~40 commits with realistic diff stats")
        print("• 3 pull requests with merge data")
        print("• 3 code reviews")
        print("\nNow you can test with: /dev-report weekly")
    else:
        print("\n❌ Seeding failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()