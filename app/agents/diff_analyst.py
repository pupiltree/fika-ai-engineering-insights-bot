import statistics
import datetime
def analyze_diff(state):
    """analyze"""
    events=state["commits"]
    
    churn_data = []
    for event in events:
        stats = event.get("stats", {})
        churn_data.append({
            "author": event["commit"]["author"]["name"],
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0)
        })
    return {**state, "churn_report": churn_data}

def analyze_prs(state):
    """Analyze PRs and compute inline DORA metrics"""
    events = state.get("pull_requests", [])
    ci_runs = state.get("ci_runs", [])
    timeframe_days = state.get("timeframe_days", 7)

    pr_data = []
    review_times = []
    cycle_times = []
    merged_prs = []

    for event in events:
        review_latency = float(event.get("review_latency_hours", 0))
        cycle_time = float(event.get("cycle_time_hours", 0))
        merged_at = event.get("merged_at")

        pr_data.append({
            "pr_number": event.get("number"),
            "user": event.get("user", {}).get("login", "Unknown"),
            "title": event.get("title", "")[:100],
            "state": event.get("state"),
            "review_latency_hours": review_latency,
            "cycle_time_hours": cycle_time,
            "files_changed": event.get("files_changed", 0),
            "additions": event.get("additions", 0),
            "deletions": event.get("deletions", 0),
            "created_at": event.get("created_at"),
            "merged_at": merged_at
        })

        if review_latency > 0:
            review_times.append(review_latency)
        if cycle_time > 0:
            cycle_times.append(cycle_time)
        if merged_at:
            merged_prs.append(event)

    #  DORA Metrics 
    lead_time = statistics.mean(cycle_times) if cycle_times else 0

    deploy_frequency = len(merged_prs) / timeframe_days if timeframe_days > 0 else 0

    total_ci = len(ci_runs)
    failed_ci = len([run for run in ci_runs if run.get("is_failure")])
    change_failure_rate = (failed_ci / total_ci) * 100 if total_ci > 0 else 0

    # MTTR calculation 
    mttr_times = []
    last_failure_time = None
    for run in sorted(ci_runs, key=lambda r: r.get("timestamp", "")):
        ts = run.get("timestamp")
        if not ts:
            continue
        run_time = datetime.fromisoformat(ts)
        if run.get("is_failure"):
            last_failure_time = run_time
        elif run.get("is_success") and last_failure_time:
            diff = (run_time - last_failure_time).total_seconds() / 3600
            mttr_times.append(diff)
            last_failure_time = None
    mttr = statistics.mean(mttr_times) if mttr_times else 0

    dora_metrics = {
        "lead_time_hours": round(lead_time, 2),
        "deploy_frequency_per_day": round(deploy_frequency, 2),
        "change_failure_rate_percent": round(change_failure_rate, 2),
        "mttr_hours": round(mttr, 2)
    }

    return {**state, "pr_insights": pr_data, "dora_metrics": dora_metrics}