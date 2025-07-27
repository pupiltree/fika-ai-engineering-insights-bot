from storage.database import Database
from datetime import datetime, timedelta
import statistics

class DiffAnalyst:
    def __init__(self):
        self.db = Database()

    def analyze(self, days=7):
        commits = self.db.get_commits(days)
        prs = self.db.get_prs(days)

        # Calculate DORA metrics
        commit_count = len(commits)
        pr_count = len([pr for pr in prs if pr.state == "closed"])

        # Fix: closed_at and created_at are already datetime objects
        cycle_times = [
            (pr.closed_at - pr.created_at).total_seconds() / 3600
            for pr in prs if pr.closed_at and pr.state == "closed"
        ]
        cycle_time = statistics.mean(cycle_times) if cycle_times else 0

        additions = sum(c.additions for c in commits)
        deletions = sum(c.deletions for c in commits)
        churn = additions + deletions
        files_changed = sum(c.files_changed for c in commits)

        # Detect churn outliers (e.g., commits with churn > mean + 2*std)
        churns = [c.additions + c.deletions for c in commits]
        mean_churn = statistics.mean(churns) if churns else 0
        std_churn = statistics.stdev(churns) if len(churns) > 1 else 0
        outliers = [
            {
                "sha": c.sha,
                "author": c.author,
                "churn": c.additions + c.deletions,
                "risk": "High" if (c.additions + c.deletions) > (mean_churn + 2 * std_churn) else "Normal"
            }
            for c in commits
            if (c.additions + c.deletions) > (mean_churn + 2 * std_churn)
        ]

        return {
            "commit_count": commit_count,
            "pr_count": pr_count,
            "cycle_time_hours": cycle_time,
            "churn": churn,
            "files_changed": files_changed,
            "outliers": outliers
        }
