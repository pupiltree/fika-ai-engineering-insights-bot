import os
import sqlite3
import statistics
import random
from datetime import datetime

import networkx as nx
import matplotlib.pyplot as plt

class DiffAnalyst:
    def __init__(self, db_path="fika_insights.db"):
        self.db_path = db_path
        os.makedirs("reports", exist_ok=True)

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
        churn_spikes = [c for c in churns if churn_std and c > avg_churn + 2 * churn_std]

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

    def forecast_churn(self, commits_metrics):
        """
        Naively forecast next week's churn per commit based on recent average churn,
        adding a small random variation to simulate uncertainty.
        """
        avg = commits_metrics.get("avg_churn", 0)
        variation = random.uniform(-0.1, 0.1) * avg
        forecast = avg + variation
        return round(forecast, 2)

    def generate_influence_graph(self):
        """
        Build and save a reviewer→author code-review influence map as a PNG.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT author, reviewer FROM pull_requests")
        interactions = cur.fetchall()
        conn.close()

        G = nx.DiGraph()
        for author, reviewer in interactions:
            if author and reviewer:
                G.add_edge(reviewer, author)

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(
            G, pos,
            with_labels=True,
            node_color="skyblue",
            node_size=2000,
            font_size=10,
            arrows=True
        )
        plt.title("Code-Review Influence Map")
        plt.tight_layout()
        path = "reports/influence_map.png"
        plt.savefig(path)
        plt.close()
        print(f"[✔] Generated {path}")
        return path

if __name__ == "__main__":
    analyst = DiffAnalyst()
    commits_metrics = analyst.analyze_commits()
    prs_metrics = analyst.analyze_pull_requests()
    forecasted_churn = analyst.forecast_churn(commits_metrics)

    print(f"[✔] Commit Metrics: {commits_metrics}")
    print(f"[✔] PR Metrics: {prs_metrics}")
    print(f"[🔮] Forecasted churn next week: {forecasted_churn} lines per commit")

    # Generate influence map for visual review
    analyst.generate_influence_graph()
