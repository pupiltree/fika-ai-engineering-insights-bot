"""
Tests for DiffAnalystAgent
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from powerbiz.agents.diff_analyst import DiffAnalystAgent


class TestDiffAnalystAgent(unittest.TestCase):
    """Test cases for DiffAnalystAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = DiffAnalystAgent()

    def test_init(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_name, "diff_analyst")
        self.assertIn("code churn", self.agent.system_prompt.lower())

    def test_calculate_churn_metrics(self):
        """Test churn metrics calculation."""
        # Mock commit data
        class MockCommit:
            def __init__(self, author_id, additions, deletions, files):
                self.developer_id = author_id
                self.additions = additions
                self.deletions = deletions
                self.changed_files = files
                self.developer = Mock()
                self.developer.github_username = f"user{author_id}"
                self.developer.name = f"User {author_id}"

        class MockPR:
            def __init__(self, additions, deletions, files, author, reviews):
                self.additions = additions
                self.deletions = deletions
                self.changed_files = files
                self.author = Mock()
                self.author.github_username = author
                self.review_count = reviews
                self.lead_time_minutes = 120
                self.title = "Test PR"
                self.id = 1

        commits = [
            MockCommit(1, 100, 50, 5),
            MockCommit(2, 200, 100, 10),
            MockCommit(1, 50, 25, 3)
        ]

        prs = [
            MockPR(30, 20, 2, "user1", 2),
            MockPR(500, 300, 15, "user2", 1)
        ]

        metrics = self.agent._calculate_churn_metrics(commits, prs)

        # Verify structure
        self.assertIn("author_churn", metrics)
        self.assertIn("team_metrics", metrics)
        self.assertIn("pr_sizes", metrics)
        self.assertIn("pr_size_distribution", metrics)

        # Verify calculations
        self.assertEqual(metrics["team_metrics"]["total_commits"], 3)
        self.assertEqual(metrics["team_metrics"]["total_additions"], 350)
        self.assertEqual(metrics["team_metrics"]["total_deletions"], 175)

    def test_calculate_defect_risk_metrics(self):
        """Test defect risk metrics calculation."""
        # Mock data
        commits = []
        prs = []

        metrics = self.agent._calculate_defect_risk_metrics(commits, prs)

        # Verify structure
        self.assertIn("high_churn_commits", metrics)
        self.assertIn("large_prs", metrics)
        self.assertIn("low_review_prs", metrics)
        self.assertIn("risk_metrics", metrics)

    def test_calculate_historical_trends(self):
        """Test historical trends calculation."""
        # Mock data
        commits = []
        prs = []

        trends = self.agent._calculate_historical_trends(commits, prs, 30)

        # Verify structure
        self.assertIn("weekly_data", trends)
        self.assertIn("churn_trend", trends)
        self.assertIn("cycle_time_trend", trends)
        self.assertIn("avg_weekly_churn", trends)
        self.assertIn("avg_cycle_time", trends)

    def test_generate_forecasts(self):
        """Test forecast generation."""
        # Mock trends data
        trends = {
            "avg_weekly_churn": 1000,
            "avg_cycle_time": 24,
            "churn_trend": 50,
            "cycle_time_trend": -2,
            "churn_values": [900, 950, 1000, 1050, 1100],
            "cycle_time_values": [26, 25, 24, 23, 22]
        }

        forecasts = self.agent._generate_forecasts(trends, 7)

        # Verify structure
        self.assertIn("predicted_weekly_churn", forecasts)
        self.assertIn("predicted_cycle_time_hours", forecasts)
        self.assertIn("churn_confidence", forecasts)
        self.assertIn("cycle_time_confidence", forecasts)
        self.assertIn("trend_direction", forecasts)

        # Verify calculations
        self.assertGreater(forecasts["predicted_weekly_churn"], 0)
        self.assertGreater(forecasts["predicted_cycle_time_hours"], 0)


if __name__ == "__main__":
    unittest.main()
