
def narrate_insights(state):
    """narrate"""

    churn_data=state["churn_report"]
    dora_metrics=state["dora_metrics"]
    print(dora_metrics)
    report="Weekly Summary \n"
    for record in churn_data:
        report+=f"{record['author']}:+{record['additions']}/-{record['deletions']}(Total: {record['total']})\n"
    
    report += "\n📈 DORA Metrics:\n"
    report += f"Lead Time for Changes: {dora_metrics.get('lead_time_hours', 0)} hours\n"
    report += f"Deployment Frequency: {dora_metrics.get('deploy_frequency_per_day', 0)} per day\n"
    report += f"Change Failure Rate: {dora_metrics.get('change_failure_rate_percent', 0)}%\n"
    report += f"Mean Time to Recovery: {dora_metrics.get('mttr_hours', 0)} hours\n"
    return {**state, "summary":report }