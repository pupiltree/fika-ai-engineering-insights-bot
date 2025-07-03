import os
from dotenv import load_dotenv
from agents.data_harvester import DataHarvesterAgent
from agents.diff_analyzer import DiffAnalyzerAgent
from agents.insight_narrator import InsightNarratorAgent
from viz.charts import (
    plot_commits_over_time,
    plot_risky_vs_safe,
    create_churn_chart,
    create_dora_chart,
    create_pr_latency_chart,
    ChartGenerationError
)
from viz.chart_config import ChartConfig
import numpy as np
from datetime import datetime, timedelta, timezone
from storage.db import init_db, insert_commits, insert_prs, insert_report

# 🔧 Load .env file
load_dotenv()

def forecast_next_week_churn_and_leadtime(commits):
    # Group commits by week
    from collections import defaultdict         
    from datetime import datetime
    weekly_churn = defaultdict(int)
    weekly_lead_times = defaultdict(list)
    for c in commits:
        dt = datetime.fromisoformat(c['date'].replace('Z', '+00:00'))
        week = dt.isocalendar()[1]
        year = dt.year
        key = (year, week)
        churn = c.get('additions', 0) + c.get('deletions', 0)
        weekly_churn[key] += churn
        weekly_lead_times[key].append(dt)
    # Sort by week
    sorted_weeks = sorted(weekly_churn.keys())
    churn_series = [weekly_churn[w] for w in sorted_weeks]
    # Moving average (last 3 weeks)
    if len(churn_series) >= 2:
        forecast_churn = int(np.mean(churn_series[-3:]))
    else:
        forecast_churn = churn_series[-1] if churn_series else 0
    # Lead time: average time between first and last commit per week
    lead_times = []
    for w in sorted_weeks:
        times = sorted(weekly_lead_times[w])
        if len(times) > 1:
            lead_times.append((times[-1] - times[0]).total_seconds() / 3600)
        else:
            lead_times.append(0)
    if len(lead_times) >= 2:
        forecast_lead = round(np.mean(lead_times[-3:]), 2)
    else:
        forecast_lead = round(lead_times[-1], 2) if lead_times else 0
    return {
        'forecast_churn': forecast_churn,
        'forecast_lead_time_hrs': forecast_lead
    }

def run_pipeline(repo: str = None, timeframe: str = "weekly"):
    # Initialize DB
    init_db()
    print(f"\n🚀 Starting Engineering Productivity Insight Pipeline for timeframe: {timeframe}\n")
    end_date = datetime.now(timezone.utc)
    if timeframe == "daily":
        start_date = end_date - timedelta(days=1)
    elif timeframe == "monthly":
        start_date = end_date - timedelta(days=30)
    else:  # weekly default
        start_date = end_date - timedelta(days=7)
    # 1. Run Data Harvester
    data_agent = DataHarvesterAgent()
    github_data = data_agent.run({"repo": repo, "start_date": start_date, "end_date": end_date})
    # Store commits and PRs in DB
    insert_commits(github_data.get('commits', []))
    insert_prs(github_data.get('prs', []))
    # 2. Run Diff Analyzer
    diff_agent = DiffAnalyzerAgent()
    analysis_data = diff_agent.run(github_data, period=timeframe)
    # Forecast next week's churn and lead time
    forecast = forecast_next_week_churn_and_leadtime(github_data.get('commits', []))

    commits = github_data.get('commits', [])
    prs = github_data.get('prs', [])
    dora_metrics = analysis_data.get('dora_metrics', {})
    author_metrics = analysis_data.get('author_metrics', {})
    config = ChartConfig()
    os.makedirs(config.output_dir, exist_ok=True)
    # Determine suffix for chart filenames
    suffix = timeframe if timeframe in ["daily", "weekly", "monthly"] else None
    # Only generate charts for weekly reports
    if timeframe == "weekly":
        if commits:
            try:
                plot_commits_over_time(commits, config, freq="W", suffix="weekly")
                plot_risky_vs_safe(commits, config, suffix="weekly")
            except ChartGenerationError as e:
                print(f"Chart error (commits): {e}")
            except Exception as e:
                print(f"Unexpected chart error (commits): {e}")
        else:
            print("No commits data available for charting.")

        if author_metrics:
            try:
                churn_chart_path = create_churn_chart(author_metrics, config, suffix="weekly")
                if churn_chart_path:
                    print(f"Churn chart saved to: {churn_chart_path}")
                else:
                    print("Churn chart was not generated.")
            except ChartGenerationError as e:
                print(f"Chart error (Churn): {e}")
            except Exception as e:
                print(f"Unexpected chart error (Churn): {e}")
        else:
            print("No author metrics available for churn charting.")

        if dora_metrics:
            try:
                dora_chart_path = create_dora_chart(dora_metrics, config, suffix="weekly")
                if dora_chart_path:
                    print(f"DORA chart saved to: {dora_chart_path}")
                else:
                    print("DORA chart was not generated.")
            except ChartGenerationError as e:
                print(f"Chart error (DORA): {e}")
            except Exception as e:
                print(f"Unexpected chart error (DORA): {e}")
        else:
            print("No DORA metrics available for charting.")

        if prs:
            try:
                pr_latency_chart_path = create_pr_latency_chart(prs, config)
                if pr_latency_chart_path:
                    print(f"PR review latency chart saved to: {pr_latency_chart_path}")
                else:
                    print("PR review latency chart was not generated.")
            except ChartGenerationError as e:
                print(f"Chart error (PRs): {e}")
            except Exception as e:
                print(f"Unexpected chart error (PRs): {e}")
        else:
            print("No PR data available for charting.")

    # Load previous period's DORA metrics for comparison
    dora_metrics_prev = None
    prev_start = start_date - (end_date - start_date)
    prev_end = start_date
    # Try to load from previous report if available
    prev_data_agent = DataHarvesterAgent()
    prev_github_data = prev_data_agent.run({"repo": repo, "start_date": prev_start, "end_date": prev_end})
    prev_diff_agent = DiffAnalyzerAgent()
    prev_analysis_data = prev_diff_agent.run(prev_github_data, period=timeframe)
    dora_metrics_prev = prev_analysis_data.get('dora_metrics', {})

    # 3. Run Insight Narrator
    insight_agent = InsightNarratorAgent()
    merged_state = {**github_data, **analysis_data, **forecast, "dora_metrics_prev": dora_metrics_prev}
    insights = insight_agent.run(merged_state, period=timeframe)
    # 4. Print or save the final insight report
    print("\n===== Engineering Report =====\n")
    print(insights.get('narrative', '❌ No narrative generated.'))
    # Save to file
    with open(os.path.join(config.output_dir, "engineering_report.txt"), "w", encoding="utf-8") as f:
        f.write(insights.get('narrative', 'No narrative'))
    # Store report in DB
    insert_report(insights.get('narrative', 'No narrative'), datetime.now(timezone.utc).isoformat())

if __name__ == "__main__":
    repo = os.getenv("GITHUB_REPO", "mock-org/mock-repo")
    print(f"🔍 Repo to analyze: {repo}")
    run_pipeline(repo)
