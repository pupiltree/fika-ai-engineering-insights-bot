def generate_narrative(metrics):
    # Map to DORA metrics, summarize findings
    summary = f"""
    Weekly Engineering Report:
    - Lead Time: {metrics['lead_time']} hrs
    - Deploy Frequency: {metrics['deploy_frequency']} per week
    - Change Failure Rate: {metrics['change_failure_rate']}%
    - MTTR: {metrics['mttr']} hrs
    """
    return summary
