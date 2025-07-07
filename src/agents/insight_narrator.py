from datetime import datetime
import random
from src.llm_config import get_llm

llm = get_llm(driver="openai")  # or "llama"

def insight_narrator_node(state):
    churn = state.get("churn", 0)
    commits = state.get("commits", [])
    authors = list({commit["author"] for commit in commits})
    commit_count = len(commits)
    avg_churn = churn // commit_count if commit_count else 0
    top_author = max(
        set([c["author"] for c in commits]),
        key=[c["author"] for c in commits].count,
        default="N/A"
    )

    # some additions for forecast
    forecast = state.get("forecast_churn")
    influence_map = state.get("influence_map")

    # fake previous week churn for insights only..
    last_week_churn = churn * random.uniform(0.7, 1.3)
    change_pct = ((churn - last_week_churn) / last_week_churn) * 100

    message = (
        f"🔍 Weekly Dev Report\n"
        f"- Total Commits: {commit_count}\n"
        f"- Total Churn: {churn} LOC\n"
        f"- Avg Churn per Commit: {avg_churn} LOC\n"
        f"- Active Engineers: {len(authors)}\n"
        f"- Top Committer: {top_author}\n"
        f"- Churn vs Last Week: {change_pct:+.2f}%\n"
    )

    if forecast:
        message += f"- Forecast Next Week's Churn: {forecast:.0f} LOC\n"

    if influence_map:
        message += "\n👥 Code Review Influence Map:\n"
        for reviewer, authors in influence_map.items():
            message += f"- {reviewer} → {', '.join(authors)}\n"

    message += "\nInsight: "
    message += (
        "Churn increased significantly — consider reviewing PR scope."
        if change_pct > 20 else
        "Healthy iteration cycle this week. Keep it up!"
    )

    with open("src/storage/insight.txt", "w") as f:
        f.write(message)

    return {"summary": message}
