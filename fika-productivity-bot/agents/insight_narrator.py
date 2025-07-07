# agents/insight_narrator.py

from typing import Dict, List
import datetime


def generate_insights(analysis: Dict) -> Dict:
    """Turn commit and PR analysis into DORA-style narrative insights."""

    insights = []

   
    pr_summary = analysis.get("pr_summary", {})
    pr_count = pr_summary.get("total_prs", 0)
    if pr_count == 0:
        insights.append(" No PR activity found. Engineering velocity might be low.")
    else:
        insights.append(f" Deployment Frequency: {pr_count} PRs merged during the period.")

    
    lead_time = pr_summary.get("avg_lead_time_hrs")
    if lead_time:
        hours = round(lead_time, 2)
        insights.append(f" Average lead time: {hours} hours from PR creation to merge.")

    
    churn_spikes = analysis.get("churn_spikes", [])
    if churn_spikes:
        insights.append(f"High churn detected in {len(churn_spikes)} commits. Possible quality risks.")
        flagged_authors = set([c["author"] for c in churn_spikes])
        insights.append(f"Authors with high churn: {', '.join(flagged_authors)}")
    else:
        insights.append(" No high-risk churn spikes detected.")

    
    commit_summary = analysis.get("commit_churn_summary", [])
    for author_data in commit_summary:
        insights.append(
            f"👤 {author_data['author']} made {author_data['commit_count']} commits "
            f"(+{author_data['additions']} / -{author_data['deletions']} lines, "
            f"{author_data['files_changed']} files changed)"
        )

    
    today = datetime.date.today()
    headline = f" Weekly Engineering Report — {today.strftime('%B %d, %Y')}"
    
    return {
        "headline": headline,
        "insights": insights
    }


# Local test
if __name__ == "__main__":
    from data_harvester import harvest_data
    from diff_analyst import analyze_diff

    raw_data = harvest_data()
    analysis = analyze_diff(raw_data)
    summary = generate_insights(analysis)

    print(summary["headline"])
    print("\n".join(summary["insights"]))
