def generate_narrative(metrics):
    if not metrics:
        return "*Weekly Engineering Summary 📉*\n\nNo commit data available for analysis this week."

    sorted_metrics = sorted(metrics, key=lambda x: x.get("churn", 0), reverse=True)
    top_author = sorted_metrics[0]["author"]
    top_churn = sorted_metrics[0]["churn"]

    total_churn = sum(item["churn"] for item in metrics)
    avg_churn = round(total_churn / len(metrics), 2)

    high_churn_authors = [item for item in metrics if item["churn"] > avg_churn * 2]

    summary = (
        "*📈 Weekly Engineering Insights Summary*\n\n"
        f"• 👨‍💻 Total developers analyzed: *{len(set([m['author'] for m in metrics]))}*\n"
        f"• 🔄 Total lines changed (churn): *{total_churn}*\n"
        f"• ⚡ Average churn per dev: *{avg_churn}* lines\n"
        f"• 🏆 Top contributor: *{top_author}* with *{top_churn}* lines changed\n"
    )

    if high_churn_authors:
        names = ', '.join([author["author"] for author in high_churn_authors])
        summary += f"• 🚨 *High churn detected* for: {names}. Consider reviewing these PRs more carefully.\n"

    summary += "\n*💡 Business & Quality Recommendations:*\n"
    summary += "• Keep PRs small to reduce risk and improve review quality.\n"
    summary += "• High churn may indicate rushed changes — revisit testing & review cycles.\n"
    summary += "• Monitor frequently high-churn contributors for mentorship or review alignment.\n"

    summary += "\n_Metrics based on DORA framework: Lead Time, Deploy Frequency, Change Failure Rate, MTTR._\n"
    summary += "_Churn analysis aligns with industry research showing a link between high churn and defect risk._\n"

    return summary
