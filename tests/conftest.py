"""
Test configuration for PowerBiz Developer Analytics
"""

import os
import sys
import pytest
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_github_client():
    """Mock GitHub client for testing."""
    client = Mock()
    client.get_repository.return_value = {
        "id": 123,
        "name": "test-repo",
        "full_name": "test-org/test-repo",
        "description": "Test repository"
    }
    client.get_commits.return_value = []
    client.get_pull_requests.return_value = []
    return client

@pytest.fixture
def sample_commit_data():
    """Sample commit data for testing."""
    return {
        "sha": "abc123",
        "commit": {
            "message": "Test commit",
            "author": {"date": "2023-01-01T12:00:00Z"}
        },
        "author": {"login": "testuser"},
        "stats": {"additions": 10, "deletions": 5, "total": 15}
    }

@pytest.fixture
def sample_pr_data():
    """Sample PR data for testing."""
    return {
        "id": 456,
        "title": "Test PR",
        "body": "Test description",
        "state": "open",
        "user": {"login": "testuser"},
        "additions": 20,
        "deletions": 10,
        "changed_files": 3,
        "created_at": "2023-01-01T12:00:00Z",
        "merged_at": None
    }
