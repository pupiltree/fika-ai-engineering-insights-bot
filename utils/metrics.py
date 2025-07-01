"""
Utility functions for calculating engineering productivity metrics and DORA stats.
"""
from typing import List, Dict, Any
from datetime import datetime

def count_commits(commits: List[Dict[str, Any]]) -> int:
    return len(commits)

def commits_per_author(commits: List[Dict[str, Any]]) -> Dict[str, int]:
    result = {}
    for c in commits:
        result[c['author']] = result.get(c['author'], 0) + 1
    return result

def pr_throughput(prs: List[Dict[str, Any]]) -> int:
    return len(prs)

def review_latency_avg(prs: List[Dict[str, Any]]) -> float:
    latencies = [pr['review_latency'] for pr in prs if pr.get('review_latency') is not None]
    return sum(latencies) / len(latencies) if latencies else 0.0

def code_churn(commits: List[Dict[str, Any]]) -> Dict[str, int]:
    additions = sum(c['additions'] for c in commits)
    deletions = sum(c['deletions'] for c in commits)
    return {'additions': additions, 'deletions': deletions}

def files_touched(commits: List[Dict[str, Any]]) -> int:
    return sum(c['changed_files'] for c in commits)

def dora_metrics(prs: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Lead time: average time from PR created to merged
    lead_times = []
    for pr in prs:
        try:
            created = datetime.fromisoformat(pr['created_at'])
            merged = datetime.fromisoformat(pr['merged_at'])
            lead_times.append((merged - created).total_seconds() / 3600)  # in hours
        except Exception:
            continue
    lead_time_avg = sum(lead_times) / len(lead_times) if lead_times else 0.0
    # Deploy frequency: number of PRs merged (proxy)
    deploy_freq = len(prs)
    # Change failure rate: percent of PRs with failed CI
    failures = [pr for pr in prs if pr.get('ci_status') == 'failure']
    change_failure_rate = len(failures) / len(prs) if prs else 0.0
    # MTTR: mean time to recovery (not enough data, so set as 0 for now)
    mttr = 0.0
    return {
        'lead_time_hours': lead_time_avg,
        'deploy_frequency': deploy_freq,
        'change_failure_rate': change_failure_rate,
        'mttr': mttr
    } 