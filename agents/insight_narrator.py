from storage.database import Database
from datetime import datetime
import statistics

class InsightNarrator:
    def __init__(self):
        self.db = Database()

    def generate_report(self, period="weekly"):
        period_days = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30
        }.get(period, 7)

        commits = self.db.get_commits(period_days)
        prs = self.db.get_prs(period_days)

        if not commits:
            return f"No commits found in the selected period ({period}).", None

        total_commits = len(commits)
        total_prs = len([pr for pr in prs if pr.state == "closed"])
        cycle_times = [
            (pr.closed_at - pr.created_at).total_seconds() / 3600
            for pr in prs if pr.closed_at and pr.state == "closed"
        ]
        avg_cycle_time = statistics.mean(cycle_times) if cycle_times else 0

        total_additions = sum(c.additions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        total_churn = total_additions + total_deletions
        files_changed = sum(c.files_changed for c in commits)

        dev_stats = {}
        for c in commits:
            dev = c.author
            if dev not in dev_stats:
                dev_stats[dev] = {"commits": 0, "additions": 0, "deletions": 0, "churn": 0}
            dev_stats[dev]["commits"] += 1
            dev_stats[dev]["additions"] += c.additions
            dev_stats[dev]["deletions"] += c.deletions
            dev_stats[dev]["churn"] += c.additions + c.deletions
        for pr in prs:
            if pr.author not in dev_stats:
                dev_stats[pr.author] = {"commits": 0, "additions": 0, "deletions": 0, "churn": 0}
            dev_stats[pr.author]["prs"] = dev_stats[pr.author].get("prs", 0) + 1

        churns = [c.additions + c.deletions for c in commits]
        mean_churn = statistics.mean(churns)
        std_churn = statistics.stdev(churns) if len(churns) > 1 else 0
        risky_commits = [
            f"- {c.sha} by {c.author} ({c.additions + c.deletions} lines)"
            for c in commits if (c.additions + c.deletions) > mean_churn + 2 * std_churn
        ]

        report_lines = [
            f"*Engineering Report ({period.capitalize()} - {datetime.now().date()}):*",
            f"- {total_commits} commits, {total_prs} PRs closed",
            f"- Avg cycle time: {avg_cycle_time:.2f} hours",
            f"- Total churn: {total_churn} lines ({files_changed} files)",
            "",
            "*👨‍💻 Developer Breakdown:*"
        ]
        for dev, stats in dev_stats.items():
            report_lines.append(
                f"- {dev}: {stats['commits']} commits"
                f", {stats.get('prs', 0)} PRs"
                f", {stats['churn']} lines changed"
            )

        if risky_commits:
            report_lines.append("\n*⚠️ High Risk Commits:*")
            report_lines.extend(risky_commits)

        return "\n".join(report_lines), None
