from agents.harvester import DataHarvester
from agents.analyst import DiffAnalyst
from agents.narrator import InsightNarrator
from reports.plot import plot_commits_vs_prs, plot_churn_per_author

def run_pipeline():
    print("[🚀] Starting pipeline...")

    # 1) DataHarvester: fetch commits/PRs
    harvester = DataHarvester()
    commits = harvester.fetch_commits()
    prs = harvester.fetch_pull_requests()
    print(f"[✔] DataHarvester: {len(commits)} commits, {len(prs)} PRs fetched.")

    # 2) DiffAnalyst: calculate metrics
    analyst = DiffAnalyst()
    commits_metrics = analyst.analyze_commits()
    prs_metrics = analyst.analyze_pull_requests()
    print(f"[✔] DiffAnalyst: Metrics calculated.")

    # 3) InsightNarrator: generate summary
    narrator = InsightNarrator()
    narrative = narrator.generate_narrative(commits_metrics, prs_metrics)
    print(f"[✔] InsightNarrator: Narrative generated.")

    # 4) Generate charts in reports/
    plot_commits_vs_prs(
        commits_count=commits_metrics["total_commits"],
        prs_count=prs_metrics["total_prs"],
    )

    # Get churn per author from the commits (just as an example calculation)
    author_churns = {}
    for c in commits:
        author, _, additions, deletions, _ = c
        churn = additions + deletions
        author_churns[author] = author_churns.get(author, 0) + churn

    author_churns_list = sorted(author_churns.items(), key=lambda x: x[0])  # sort by author
    plot_churn_per_author(author_churns_list)

    return {
        "commits_metrics": commits_metrics,
        "prs_metrics": prs_metrics,
        "narrative": narrative,
    }

if __name__ == "__main__":
    result = run_pipeline()
    print("\n[📊] Final Narrative:\n")
    print(result["narrative"])
