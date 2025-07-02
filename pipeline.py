from agents.harvester import DataHarvester
from agents.analyst import DiffAnalyst
from agents.narrator import InsightNarrator
from reports.plot import plot_commits_vs_prs, plot_churn_per_author
import os

def run_pipeline():
    print("[🚀] Starting pipeline...")

    # 1) DataHarvester: fetch commits & PRs
    harvester = DataHarvester()
    commits = harvester.fetch_commits()
    prs = harvester.fetch_pull_requests()
    print(f"[✔] DataHarvester: {len(commits)} commits, {len(prs)} PRs fetched.")

    # 2) DiffAnalyst: calculate metrics and forecast churn
    analyst = DiffAnalyst()
    commits_metrics = analyst.analyze_commits()
    prs_metrics = analyst.analyze_pull_requests()
    forecasted_churn = analyst.forecast_churn(commits_metrics)
    print(f"[✔] DiffAnalyst: Metrics calculated. Forecasted churn: {forecasted_churn}")

    # 3) InsightNarrator: generate summary (now accepts forecast)
    narrator = InsightNarrator()
    narrative = narrator.generate_narrative(commits_metrics, prs_metrics, forecasted_churn)
    print(f"[✔] InsightNarrator: Narrative generated.")

    # 4) Generate standard charts in reports/
    plot_commits_vs_prs(
        commits_count=commits_metrics["total_commits"],
        prs_count=prs_metrics["total_prs"],
    )

    # Aggregate churn per author for plotting
    author_churns = {}
    for author, _, additions, deletions, _ in commits:
        churn = additions + deletions
        author_churns[author] = author_churns.get(author, 0) + churn

    author_churns_list = sorted(author_churns.items(), key=lambda x: x[0])
    plot_churn_per_author(author_churns_list)

    # 5) Generate code-review influence map
    influence_map_path = analyst.generate_influence_graph()

    return {
        "commits_metrics": commits_metrics,
        "prs_metrics": prs_metrics,
        "forecasted_churn": forecasted_churn,
        "narrative": narrative,
        "charts": [
            "reports/commits_vs_prs.png",
            "reports/churn_per_author.png",
            influence_map_path
        ]
    }

if __name__ == "__main__":
    result = run_pipeline()
    print("\n[📊] Final Narrative:\n")
    print(result["narrative"])
    print(f"\n🔮 Forecasted Churn Next Week: {result['forecasted_churn']} lines per commit")
    print("\n[📁] Charts generated:")
    for path in result["charts"]:
        print(f"  - {path}")
