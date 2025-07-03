"""
Tests for DataHarvesterAgent
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from powerbiz.agents.data_harvester import DataHarvesterAgent


class TestDataHarvesterAgent(unittest.TestCase):
    """Test cases for DataHarvesterAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = DataHarvesterAgent()

    def test_init(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_name, "data_harvester")
        self.assertIsNotNone(self.agent.harvester)

    def test_prepare_repo_stats(self):
        """Test repository statistics preparation."""
        # Mock data
        mock_commits = []
        mock_prs = []
        mock_builds = []

        # Call the method
        stats = self.agent._prepare_repo_stats(mock_commits, mock_prs, mock_builds)

        # Verify structure
        self.assertIn("commit_stats", stats)
        self.assertIn("author_stats", stats)
        self.assertIn("pr_stats", stats)
        self.assertIn("ci_stats", stats)
        self.assertIn("dora_metrics", stats)

    def test_calculate_pr_sizes(self):
        """Test PR size calculation."""
        # Mock PR data
        class MockPR:
            def __init__(self, additions, deletions):
                self.additions = additions
                self.deletions = deletions

        prs = [
            MockPR(5, 5),    # xs (10 total)
            MockPR(30, 20),  # small (50 total)
            MockPR(100, 50), # medium (150 total)
            MockPR(600, 400) # large (1000 total)
        ]

        sizes = self.agent._calculate_pr_sizes(prs)

        self.assertEqual(sizes["xs"], 1)
        self.assertEqual(sizes["small"], 1)
        self.assertEqual(sizes["medium"], 1)
        self.assertEqual(sizes["large"], 1)
        self.assertEqual(sizes["xl"], 0)

    def test_calculate_dora_metrics_empty(self):
        """Test DORA metrics with empty data."""
        metrics = self.agent._calculate_dora_metrics([], [], [], [], [])

        self.assertEqual(metrics["deployment_frequency"], 0)
        self.assertEqual(metrics["lead_time_for_changes"], 0)
        self.assertEqual(metrics["mean_time_to_recovery"], 0)
        self.assertEqual(metrics["change_failure_rate"], 0)


if __name__ == "__main__":
    unittest.main()
