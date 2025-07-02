import sqlite3
import statistics
from datetime import datetime

class DiffAnalyst:
    def __init__(self, db_path="fika_insights.db"):
        self.db_path = db_path

    def analyze_commits(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT additions, deletions FROM commits")
        data = cur.fetchall()
        conn.close()

        churns = [add + del_ for add, del_ in data]
        total_churn = sum(churns)
        avg_churn = statistics.mean(churns) if churns else 0
        churn_std = statistics.stdev(churns) if len(churns) > 1 else 0
        churn_spikes = [c for c in churns if churn_std and c > avg_churn + 2*churn_std]

        return {
            "total_commits": len(churns),
            "total_churn": total_churn,
            "avg_churn": avg_churn,
            "churn_spikes": len(churn_spikes)
        }

    def analyze_pull_requests(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT opened_at, closed_at FROM pull_requests")
        data = cur.fetchall()
        conn.close()

        review_latencies = []
        for opened, closed in data:
            o = datetime.fromisoformat(opened)
            c = datetime.fromisoformat(closed)
            latency = (c - o).total_seconds() / 3600  # hours
            review_latencies.append(latency)

        avg_review_latency = statistics.mean(review_latencies) if review_latencies else 0

        return {
            "total_prs": len(review_latencies),
            "avg_review_latency_hours": avg_review_latency,
        }

if __name__ == "__main__":
    analyst = DiffAnalyst()
    commits_metrics = analyst.analyze_commits()
    prs_metrics = analyst.analyze_pull_requests()
    print(f"[✔] Commit Metrics: {commits_metrics}")
    print(f"[✔] PR Metrics: {prs_metrics}")
