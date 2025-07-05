from typing import Dict
import json
import os

def generate_insight_summary(state: Dict) -> Dict:
    metrics = state.get("metrics", {})
    author_stats = metrics.get("author_stats", {})
    high_churn_commits = metrics.get("high_churn_commits", [])

    time_window = state.get("time_window", "weekly")
    summary_lines = [f"📊 *{time_window.capitalize()} Dev Report Summary*"]

    # 📌 Author-level summary
    for author, stats in author_stats.items():
        summary_lines.append(
            f"👤 *{author}*: {stats['commits']} commits, "
            f"+{stats['additions']} / -{stats['deletions']} lines"
        )

    # 🚨 High churn commit warnings
    if high_churn_commits:
        summary_lines.append("\n⚠️ *High Churn Commits Detected:*")
        for c in high_churn_commits:
            summary_lines.append(
                f"- {c['author']} on {c['date']}: +{c['additions']} / -{c['deletions']}"
            )
    else:
        summary_lines.append("\n✅ No high-churn commits this week.")

    # 🥇 Top contributor
    if author_stats:
        top_author = max(author_stats.items(), key=lambda x: x[1]["commits"])[0]
        summary_lines.append(f"\n🏅 *Top Contributor:* {top_author}")

    # 📊 DORA Metrics (optional)
    dora_section = []
    if any(k in metrics for k in ["cycle_time_days", "deploy_frequency", "change_failure_rate", "mean_time_to_restore"]):
        dora_section.append("\n📈 *DORA Metrics:*")
        if "cycle_time_days" in metrics:
            dora_section.append(f"- ⏱️ *Cycle Time:* {metrics['cycle_time_days']} days")
        if "deploy_frequency" in metrics:
            dora_section.append(f"- 🚀 *Deploy Frequency:* {metrics['deploy_frequency']} times")
        if "change_failure_rate" in metrics:
            percent = round(metrics["change_failure_rate"] * 100, 1)
            dora_section.append(f"- ❌ *Change Failure Rate:* {percent}%")
        if "mean_time_to_restore" in metrics:
            dora_section.append(f"- 🔁 *MTTR:* {metrics['mean_time_to_restore']} hrs")

    summary_lines.extend(dora_section)

    result = {**state, "insight_summary": "\n".join(summary_lines)}

    os.makedirs("logs", exist_ok=True)
    with open("logs/agent_logs.txt", "a") as log:
        log.write("[generate_insight_summary] INPUT:\n")
        log.write(json.dumps(state, indent=2) + "\n")
        log.write("[generate_insight_summary] OUTPUT:\n")
        log.write(json.dumps(result, indent=2) + "\n\n")

    return result
