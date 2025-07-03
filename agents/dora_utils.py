# agents/dora_utils.py
from datetime import datetime

def calculate_dora_metrics(prs: list) -> dict:
    if not prs:
        return {"lead_time": 0, "deploy_frequency": 0, "change_failure_rate": 0, "mttr": 0}

    lead_times = [
        (datetime.fromisoformat(pr["merged_at"].replace('Z', '')) -
         datetime.fromisoformat(pr["created_at"].replace('Z', ''))).total_seconds() / 3600
        for pr in prs
    ]
    lead_time = round(sum(lead_times) / len(lead_times), 2)

    deploys = len(prs)
    days = max(
        (datetime.fromisoformat(pr["merged_at"].replace('Z', '')) for pr in prs),
        default=datetime.now()
    ) - min(
        (datetime.fromisoformat(pr["merged_at"].replace('Z', '')) for pr in prs),
        default=datetime.now()
    )
    deploy_frequency = round(deploys / (days.days / 7 or 1), 2)

    failures = sum(1 for pr in prs if pr.get("ci_status") == "failure")
    change_failure_rate = round((failures / len(prs)) * 100, 2)

    mttr = round(2.0, 2)  # Static / simulated value for now

    return {
        "lead_time": lead_time,
        "deploy_frequency": deploy_frequency,
        "change_failure_rate": change_failure_rate,
        "mttr": mttr
    }
