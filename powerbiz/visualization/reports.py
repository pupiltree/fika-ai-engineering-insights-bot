"""
Report generation utilities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from powerbiz.visualization.charts import (
    generate_commit_activity_chart,
    generate_code_churn_chart,
    generate_pr_lead_time_chart,
    generate_dora_metrics_chart,
    generate_author_contributions_chart,
    generate_pr_size_distribution_chart
)

logger = logging.getLogger(__name__)

def generate_daily_report_blocks(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate Slack blocks for a daily report.
    
    Args:
        report: Daily report data
        
    Returns:
        List of Slack blocks
    """
    metrics = report["metrics"]
    narrative = report["narrative"]["sections"]
    repository = report["repository"]
    date = report["date"]
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Daily Engineering Report: {repository.full_name}",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Date: {date}",
                    "emoji": True
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Daily Summary*\n{narrative['summary']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*DORA Metrics Update*\n{narrative['dora_metrics']}"
            }
        }
    ]
    
    # Add commit activity chart if we have data
    daily_commits = metrics["commit_metrics"].get("daily_commits", {})
    if daily_commits:
        commit_chart_base64 = generate_commit_activity_chart(
            daily_commits, title=f"Commit Activity: {date}"
        )
        
        blocks.append({
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Commit Activity",
                "emoji": True
            },
            "image_url": f"data:image/png;base64,{commit_chart_base64}",
            "alt_text": "Commit Activity Chart"
        })
    
    # Add developer contributions chart if we have data
    if metrics["author_stats"]:
        contrib_chart_base64 = generate_author_contributions_chart(
            metrics["author_stats"], title=f"Developer Contributions: {date}"
        )
        
        blocks.append({
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Developer Contributions",
                "emoji": True
            },
            "image_url": f"data:image/png;base64,{contrib_chart_base64}",
            "alt_text": "Developer Contributions Chart"
        })
    
    # Add highlights and concerns
    blocks.extend([
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Highlights and Concerns*\n{narrative['highlights_concerns']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommendations*\n{narrative['recommendations']}"
            }
        }
    ])
    
    # Add metrics summary
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Commits:* {metrics['commit_metrics']['total_commits']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*PRs Opened:* {metrics['pr_metrics']['new_prs']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*PRs Merged:* {metrics['pr_metrics']['merged_prs']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Deployments:* {metrics['deployment_metrics']['deployments']}"
                }
            ]
        }
    ])
    
    return blocks

def generate_weekly_report_blocks(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate Slack blocks for a weekly report.
    
    Args:
        report: Weekly report data
        
    Returns:
        List of Slack blocks
    """
    metrics = report["metrics"]
    narrative = report["narrative"]["sections"]
    repository = report["repository"]
    start_date = report["start_date"]
    end_date = report["end_date"]
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Weekly Engineering Report: {repository.full_name}",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Period: {start_date} to {end_date}",
                    "emoji": True
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Executive Summary*\n{narrative['executive_summary']}"
            }
        }
    ]
    
    # Add DORA metrics radar chart
    dora_chart_base64 = generate_dora_metrics_chart(
        metrics["dora_metrics"], title="DORA Metrics Performance"
    )
    
    blocks.append({
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": "DORA Metrics",
            "emoji": True
        },
        "image_url": f"data:image/png;base64,{dora_chart_base64}",
        "alt_text": "DORA Metrics Chart"
    })
    
    # Add DORA metrics analysis
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*DORA Metrics Analysis*\n{narrative['dora_metrics']}"
        }
    })
    
    # Add commit activity chart if we have data
    daily_commits = metrics["commit_metrics"].get("daily_commits", {})
    if daily_commits:
        commit_chart_base64 = generate_commit_activity_chart(
            daily_commits, title=f"Commit Activity: {start_date} to {end_date}"
        )
        
        blocks.append({
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Commit Activity",
                "emoji": True
            },
            "image_url": f"data:image/png;base64,{commit_chart_base64}",
            "alt_text": "Commit Activity Chart"
        })
    
    # Add developer contributions chart if we have data
    if metrics["author_stats"]:
        contrib_chart_base64 = generate_author_contributions_chart(
            metrics["author_stats"], title=f"Developer Contributions: {start_date} to {end_date}"
        )
        
        blocks.append({
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Developer Contributions",
                "emoji": True
            },
            "image_url": f"data:image/png;base64,{contrib_chart_base64}",
            "alt_text": "Developer Contributions Chart"
        })
    
    # Add team performance section
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Team Performance*\n{narrative['team_performance']}"
        }
    })
    
    # Add engineering health section
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Engineering Health*\n{narrative['engineering_health']}"
        }
    })
    
    # Add PR size distribution chart if available
    if "pr_size_distribution" in metrics:
        pr_size_chart_base64 = generate_pr_size_distribution_chart(
            metrics["pr_size_distribution"], title="Pull Request Size Distribution"
        )
        
        blocks.append({
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "PR Size Distribution",
                "emoji": True
            },
            "image_url": f"data:image/png;base64,{pr_size_chart_base64}",
            "alt_text": "PR Size Distribution Chart"
        })
    
    # Add recommendations
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Key Recommendations*\n{narrative['recommendations']}"
        }
    })
    
    # Add metrics summary
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Commits:* {metrics['commit_metrics']['total_commits']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*PRs Merged:* {metrics['pr_metrics']['merged_prs']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Lead Time:* {metrics['dora_metrics']['lead_time_hours']:.1f} hours"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Deployments:* {metrics['deployment_metrics']['deployments']}"
                }
            ]
        }
    ])
    
    return blocks
