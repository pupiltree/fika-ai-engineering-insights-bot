class InsightNarrator:
    def __init__(self):
        pass

    def generate_narrative(self, commits_metrics, prs_metrics, forecasted_churn):
        """
        Generate a DORA-aligned narrative including a forecast of next week's churn.
        """
        summary = [
            f"🚀 *Deployment Frequency:* {prs_metrics['total_prs']} PRs merged in this period.",
            f"⏱ *Lead Time for Changes:* Average review latency is {prs_metrics['avg_review_latency_hours']:.1f} hours.",
            f"📈 *Change Churn:* Average churn per commit is {commits_metrics['avg_churn']:.1f} lines.",
            f"⚠️ *Change Failure Risk:* {commits_metrics['churn_spikes']} churn spikes detected (possible defect risk).",
            f"🔮 *Forecasted Churn Next Week:* ~{forecasted_churn} lines per commit."
        ]
        return "\n".join(summary)

if __name__ == "__main__":
    # Example test data
    commits_metrics = {
        "total_commits": 50,
        "total_churn": 21331,
        "avg_churn": 426.6,
        "churn_spikes": 0
    }
    prs_metrics = {
        "total_prs": 20,
        "avg_review_latency_hours": 23.15
    }
    forecasted_churn = 430.12

    narrator = InsightNarrator()
    narrative = narrator.generate_narrative(commits_metrics, prs_metrics, forecasted_churn)
    print("[✔] Generated Insight Narrative:")
    print(narrative)
