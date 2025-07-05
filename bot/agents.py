# agents.py
# Stubs for LangChain + LangGraph agents
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from github import (
    fetch_commits, fetch_commit_details, fetch_prs,
    fetch_merged_prs_last_week, fetch_review_latency,
    fetch_cycle_time, fetch_ci_failures, fetch_prs_with_reviews
)
import numpy as np
from typing import TypedDict
import logging
import json
from datetime import datetime
from forecasting import forecast_cycle_time, forecast_churn, generate_forecast_summary
from influence_map import create_influence_map

# Set up logging
logging.basicConfig(
    filename='agent_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_agent_interaction(agent_name: str, input_data: dict, output_data: dict):
    """Log agent inputs and outputs for auditability."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'agent': agent_name,
        'input': input_data,
        'output': output_data
    }
    logging.info(f"Agent Interaction: {json.dumps(log_entry, indent=2)}")

def calculate_dora_metrics(analytics):
    """Calculate DORA metrics from analytics data."""
    lead_time = analytics.get('review_latency', 0)  # hours
    
    deployment_freq = analytics.get('pr_throughput', 0)  # PRs per week
    
    # Change Failure Rate (simplified: CI failures / total PRs)
    total_prs = analytics.get('pr_count', 0)
    ci_failures = analytics.get('ci_failures', 0)
    change_failure_rate = (ci_failures / total_prs * 100) if total_prs > 0 else 0
    
    # MTTR (simplified: assume 2 hours for now, could be enhanced with incident data)
    mttr = 2.0  # hours
    
    return {
        'lead_time': lead_time,
        'deployment_frequency': deployment_freq,
        'change_failure_rate': change_failure_rate,
        'mttr': mttr
    }

def get_dora_performance_category(dora_metrics: dict) -> str:
    """Categorize performance based on DORA metrics."""
    if (dora_metrics['lead_time'] < 1 and 
        dora_metrics['deployment_frequency'] > 1 and 
        dora_metrics['change_failure_rate'] < 15 and 
        dora_metrics['mttr'] < 1):
        return "ELITE"
    elif (dora_metrics['lead_time'] < 1 and 
          dora_metrics['deployment_frequency'] > 1 and 
          dora_metrics['change_failure_rate'] < 15 and 
          dora_metrics['mttr'] < 24):
        return "HIGH"
    elif (dora_metrics['lead_time'] < 1 and 
          dora_metrics['deployment_frequency'] > 1 and 
          dora_metrics['change_failure_rate'] < 15 and 
          dora_metrics['mttr'] < 168):
        return "MEDIUM"
    else:
        return "LOW"

def log_dora_metrics(dora_metrics: dict):
    """Log DORA metrics separately for analysis."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'dora_metrics': dora_metrics,
        'performance_category': get_dora_performance_category(dora_metrics)
    }
    logging.info(f"DORA Metrics: {json.dumps(log_entry, indent=2)}")

class AgentState(TypedDict, total=False):
    commit_data: list
    pr_count: int
    pr_throughput: int
    review_latency: float
    cycle_time: float
    ci_failures: int
    authors: dict
    spikes: list
    summary: str
    dora_metrics: dict
    forecast_summary: str
    influence_summary: str
    influence_chart: object

def data_harvester_node(state: AgentState) -> AgentState:
    """Harvests commit and PR data from GitHub and computes basic metrics."""
    # Log input
    log_agent_interaction("DataHarvester", {"input_state": state}, {})
    
    commits = fetch_commits(per_page=10)
    commit_data = []
    for commit in commits:
        # Always use GitHub username if available
        author = commit['author']['login'] if commit['author'] else commit['commit']['author']['name']
        sha = commit['sha']
        details = fetch_commit_details(sha)
        if details is None:
            continue
        additions = details['stats']['additions']
        deletions = details['stats']['deletions']
        files = len(details['files'])
        timestamp = details['commit']['author']['date']
        commit_data.append((None, 'commit', author, additions, deletions, files, timestamp))
    prs = fetch_prs(per_page=10)
    pr_count = len(prs)
    merged_prs_last_week = fetch_merged_prs_last_week()
    pr_throughput = len(merged_prs_last_week)
    review_latency = fetch_review_latency(prs)
    cycle_time = fetch_cycle_time(prs)
    ci_failures = fetch_ci_failures()
    
    result: AgentState = {
        "commit_data": commit_data,
        "pr_count": pr_count,
        "pr_throughput": pr_throughput,
        "review_latency": review_latency,
        "cycle_time": cycle_time,
        "ci_failures": ci_failures
    }
    
    # Log output
    log_agent_interaction("DataHarvester", {}, {"output_state": result})
    return result

def diff_analyst_node(state: AgentState) -> AgentState:
    """Analyzes commit data for churn, spikes, and aggregates metrics."""
    # Log input
    log_agent_interaction("DiffAnalyst", {"input_state": state}, {})
    
    commit_data = state.get("commit_data", [])
    pr_count = state.get("pr_count", 0)
    pr_throughput = state.get("pr_throughput", 0)
    review_latency = state.get("review_latency", 0.0)
    cycle_time = state.get("cycle_time", 0.0)
    ci_failures = state.get("ci_failures", 0)
    authors = {}
    churns = []
    spikes = []
    for row in commit_data:
        author = row[2]
        additions = row[3]
        deletions = row[4]
        churn = additions + deletions
        churns.append(churn)
        authors.setdefault(author, {'commits': 0, 'additions': 0, 'deletions': 0, 'spikes': 0})
        authors[author]['commits'] += 1
        authors[author]['additions'] += additions
        authors[author]['deletions'] += deletions
    mean_churn = np.mean(churns) if churns else 0
    std_churn = np.std(churns) if churns else 0
    for row in commit_data:
        author = row[2]
        additions = row[3]
        deletions = row[4]
        churn = additions + deletions
        if churn > mean_churn + 2 * std_churn:
            authors[author]['spikes'] += 1
            spikes.append({'author': author, 'churn': churn})
    
    result: AgentState = {
        "authors": authors,
        "pr_count": pr_count,
        "pr_throughput": pr_throughput,
        "review_latency": review_latency,
        "cycle_time": cycle_time,
        "ci_failures": ci_failures,
        "spikes": spikes
    }
    
    # Log output
    log_agent_interaction("DiffAnalyst", {}, {"output_state": result})
    return result

def insight_narrator_node(state: AgentState) -> AgentState:
    """Generates a human-readable summary and DORA metrics from analytics."""
    # Log input
    log_agent_interaction("InsightNarrator", {"input_state": state}, {})
    
    analytics = state
    lines = []
    
    # Per-author stats
    for author, stats in analytics.get('authors', {}).items():
        spike_msg = f" (⚠️ {stats['spikes']} spike commits - higher defect risk!)" if stats['spikes'] > 0 else ""
        lines.append(
            f"{author}: Commits: {stats['commits']}, Additions: {stats['additions']}, Deletions: {stats['deletions']}{spike_msg}"
        )
    
    # Basic metrics
    lines.append(f"Total PRs: {analytics.get('pr_count', 0)}")
    lines.append(f"PR Throughput (last 7 days): {analytics.get('pr_throughput', 0)}")
    lines.append(f"Review Latency (avg, hrs): {analytics.get('review_latency', 0.0):.2f}")
    lines.append(f"Cycle Time (avg, hrs): {analytics.get('cycle_time', 0.0):.2f}")
    lines.append(f"CI Failures (last week): {analytics.get('ci_failures', 0)}")
    
    # DORA Metrics
    dora_metrics = calculate_dora_metrics(analytics)
    performance_category = get_dora_performance_category(dora_metrics)
    lines.append("\n**DORA Metrics:**")
    lines.append(f"Lead Time for Changes: {dora_metrics['lead_time']:.2f} hours")
    lines.append(f"Deployment Frequency: {dora_metrics['deployment_frequency']} per week")
    lines.append(f"Change Failure Rate: {dora_metrics['change_failure_rate']:.1f}%")
    lines.append(f"Mean Time to Recovery: {dora_metrics['mttr']:.1f} hours")
    lines.append(f"Performance Category: {performance_category}")
    
    # Forecasting
    try:
        prs = fetch_prs(per_page=50)  # Get more PRs for forecasting
        cycle_time_forecast = forecast_cycle_time(prs)
        churn_forecast = forecast_churn(analytics.get('commit_data', []))
        forecast_summary = generate_forecast_summary(cycle_time_forecast, churn_forecast)
    except Exception as e:
        forecast_summary = f"Forecasting unavailable: {str(e)}"
    
    # Influence Map
    try:
        prs_with_reviews = fetch_prs_with_reviews(per_page=50)  # Get PRs with review data
        influence_chart, influence_summary = create_influence_map(prs_with_reviews)
        if influence_chart:
            # Store chart for later use in main.py
            analytics['influence_chart'] = influence_chart
    except Exception as e:
        influence_summary = f"Influence map unavailable: {str(e)}"
    
    summary = '\n'.join(lines)
    
    # Log DORA metrics
    log_dora_metrics(dora_metrics)
    
    result: AgentState = {**analytics, "summary": summary, "dora_metrics": dora_metrics, 
                         "forecast_summary": forecast_summary, "influence_summary": influence_summary}
    
    # Log output
    log_agent_interaction("InsightNarrator", {}, {"output_state": result})
    return result

# LangGraph orchestration
# Use AgentState as the state schema for MVP
graph = StateGraph(AgentState)
graph.add_node("harvest", data_harvester_node)
graph.add_node("analyze", diff_analyst_node)
graph.add_node("narrate", insight_narrator_node)
graph.add_edge("__start__", "harvest")
graph.add_edge("harvest", "analyze")
graph.add_edge("analyze", "narrate")
graph.add_edge("narrate", END)
workflow = graph.compile()