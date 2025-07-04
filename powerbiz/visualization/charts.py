"""
Visualization utilities for engineering metrics
"""

import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import io
import base64

logger = logging.getLogger(__name__)

def generate_commit_activity_chart(
    daily_commits: Dict[str, int],
    title: str = "Commit Activity"
) -> str:
    """Generate a chart showing daily commit activity.
    
    Args:
        daily_commits: Dictionary mapping date strings to commit counts
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # Convert to DataFrame for easier plotting
    dates = []
    counts = []
    for date_str, count in sorted(daily_commits.items()):
        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        counts.append(count)
    
    df = pd.DataFrame({
        'date': dates,
        'commits': counts
    })
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars
    ax.bar(df['date'], df['commits'], color='#4285F4', alpha=0.7)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Commits')
    ax.set_title(title)
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    fig.tight_layout()
    
    # Convert to base64
    return figure_to_base64(fig)

def generate_code_churn_chart(
    commits_data: List[Dict[str, Any]],
    title: str = "Code Churn Over Time"
) -> str:
    """Generate a chart showing code churn over time.
    
    Args:
        commits_data: List of commit data with additions and deletions
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # Prepare data
    dates = []
    additions = []
    deletions = []
    
    for commit in sorted(commits_data, key=lambda x: x['date']):
        dates.append(commit['date'])
        additions.append(commit['additions'])
        deletions.append(-commit['deletions'])  # Negative for visualization
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot bars
    ax.bar(dates, additions, color='green', alpha=0.7, label='Additions')
    ax.bar(dates, deletions, color='red', alpha=0.7, label='Deletions')
    
    # Format x-axis
    if dates:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
    
    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Lines of Code')
    ax.set_title(title)
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    fig.tight_layout()
    
    # Convert to base64
    return figure_to_base64(fig)

def generate_pr_lead_time_chart(
    pr_data: List[Dict[str, Any]],
    title: str = "Pull Request Lead Times"
) -> str:
    """Generate a chart showing PR lead times.
    
    Args:
        pr_data: List of PR data with lead times
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # Filter PRs with lead time data
    pr_data = [pr for pr in pr_data if pr.get('lead_time_hours') is not None]
    
    if not pr_data:
        # Create empty chart if no data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No lead time data available", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
        ax.set_title(title)
        return figure_to_base64(fig)
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(pr_data)
    
    # Sort by date if available
    if 'created_at' in df.columns:
        df = df.sort_values('created_at')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot scatter and trend line
    ax.scatter(range(len(df)), df['lead_time_hours'], alpha=0.7, color='#4285F4')
    
    # Add trend line
    z = np.polyfit(range(len(df)), df['lead_time_hours'], 1)
    p = np.poly1d(z)
    ax.plot(range(len(df)), p(range(len(df))), "r--", alpha=0.7)
    
    # Add labels and title
    if 'created_at' in df.columns:
        ax.set_xlabel('Pull Requests (by creation date)')
    else:
        ax.set_xlabel('Pull Requests')
    ax.set_ylabel('Lead Time (hours)')
    ax.set_title(title)
    
    # Add horizontal line for average
    avg_lead_time = df['lead_time_hours'].mean()
    ax.axhline(y=avg_lead_time, color='g', linestyle='-', alpha=0.7)
    ax.text(len(df) * 0.02, avg_lead_time * 1.05, f'Average: {avg_lead_time:.1f} hours', 
            color='g')
    
    # Add grid
    ax.grid(linestyle='--', alpha=0.7)
    
    # Adjust layout
    fig.tight_layout()
    
    # Convert to base64
    return figure_to_base64(fig)

def generate_dora_metrics_chart(
    metrics: Dict[str, Any],
    title: str = "DORA Metrics Performance"
) -> str:
    """Generate a radar chart showing DORA metrics performance.
    
    Args:
        metrics: Dictionary with DORA metrics
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # DORA metrics and their performance levels
    # For each metric, define the thresholds for low, medium, high, elite
    # and whether higher is better (True) or lower is better (False)
    dora_definitions = {
        'lead_time_hours': {
            'label': 'Lead Time for Changes (hours)',
            'thresholds': [720, 168, 24],  # 30 days, 7 days, 1 day in hours
            'higher_is_better': False
        },
        'deployment_frequency_per_day': {
            'label': 'Deployment Frequency (per day)',
            'thresholds': [0.033, 0.14, 1],  # monthly, weekly, daily
            'higher_is_better': True
        },
        'change_failure_rate': {
            'label': 'Change Failure Rate',
            'thresholds': [0.45, 0.3, 0.15],  # 45%, 30%, 15%
            'higher_is_better': False
        },
        'mttr_hours': {
            'label': 'MTTR (hours)',
            'thresholds': [720, 168, 24],  # 30 days, 7 days, 1 day in hours
            'higher_is_better': False
        }
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    
    # Number of metrics
    N = len(dora_definitions)
    
    # Angles for each metric
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    # Performance levels (0=low, 1=medium, 2=high, 3=elite)
    performance_levels = []
    labels = []
    
    for metric_key, definition in dora_definitions.items():
        value = metrics.get(metric_key, 0)
        thresholds = definition['thresholds']
        higher_is_better = definition['higher_is_better']
        
        level = 0  # Default to low
        if higher_is_better:
            for i, threshold in enumerate(thresholds):
                if value >= threshold:
                    level = i + 1
        else:
            for i, threshold in enumerate(thresholds):
                if value <= threshold:
                    level = 3 - i
        
        performance_levels.append(level)
        labels.append(definition['label'])
    
    # Normalize to 0-1 scale
    values = [level / 3 for level in performance_levels]
    values += values[:1]  # Close the loop
    
    # Add angles for labels
    angles_labels = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    
    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2, color='#4285F4')
    ax.fill(angles, values, alpha=0.25, color='#4285F4')
    
    # Set category labels
    ax.set_xticks(angles_labels)
    ax.set_xticklabels(labels)
    
    # Set radial ticks
    ax.set_yticks([0, 0.33, 0.66, 1])
    ax.set_yticklabels(['Low', 'Medium', 'High', 'Elite'])
    
    # Remove radial lines
    ax.yaxis.grid(False)
    
    # Add title
    plt.title(title, y=1.1)
    
    # Adjust layout
    fig.tight_layout()
    
    # Convert to base64
    return figure_to_base64(fig)

def generate_author_contributions_chart(
    author_stats: Dict[str, Dict[str, Any]],
    title: str = "Developer Contributions"
) -> str:
    """Generate a chart showing developer contributions.
    
    Args:
        author_stats: Dictionary mapping usernames to contribution stats
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # Convert to DataFrame for easier plotting
    data = []
    for username, stats in author_stats.items():
        data.append({
            'username': username,
            'commits': stats['commit_count'],
            'additions': stats['additions'],
            'deletions': stats['deletions']
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        # Create empty chart if no data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No contributor data available", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
        ax.set_title(title)
        return figure_to_base64(fig)
    
    # Sort by total changes
    df['total_changes'] = df['additions'] + df['deletions']
    df = df.sort_values('total_changes', ascending=False)
    
    # Limit to top 10 contributors
    df = df.head(10)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Plot commits
    bars1 = ax1.bar(df['username'], df['commits'], color='#4285F4', alpha=0.7)
    ax1.set_xlabel('Developer')
    ax1.set_ylabel('Number of Commits')
    ax1.set_title(f'Commits by Developer')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add commit count labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # Plot code changes (additions and deletions)
    bar_width = 0.35
    r1 = np.arange(len(df))
    r2 = [x + bar_width for x in r1]
    
    bars2 = ax2.bar(r1, df['additions'], width=bar_width, color='green', alpha=0.7, label='Additions')
    bars3 = ax2.bar(r2, df['deletions'], width=bar_width, color='red', alpha=0.7, label='Deletions')
    
    ax2.set_xlabel('Developer')
    ax2.set_ylabel('Lines of Code')
    ax2.set_title(f'Code Changes by Developer')
    ax2.set_xticks([r + bar_width/2 for r in range(len(df))])
    ax2.set_xticklabels(df['username'])
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax2.legend()
    
    # Adjust layout
    fig.suptitle(title, fontsize=16)
    fig.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Convert to base64
    return figure_to_base64(fig)

def generate_pr_size_distribution_chart(
    pr_size_distribution: Dict[str, int],
    title: str = "Pull Request Size Distribution"
) -> str:
    """Generate a chart showing PR size distribution.
    
    Args:
        pr_size_distribution: Dictionary mapping size categories to counts
        title: Chart title
        
    Returns:
        Base64 encoded PNG image
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Categories and counts
    categories = ['small', 'medium', 'large', 'extra_large']
    labels = ['Small (<50)', 'Medium (50-300)', 'Large (300-1000)', 'Extra Large (>1000)']
    counts = [pr_size_distribution.get(cat, 0) for cat in categories]
    
    # Define colors
    colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
    
    # Plot bars
    bars = ax.bar(labels, counts, color=colors, alpha=0.7)
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # Add labels and title
    ax.set_xlabel('Pull Request Size (lines changed)')
    ax.set_ylabel('Number of PRs')
    ax.set_title(title)
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    fig.tight_layout()
    
    # Convert to base64
    return figure_to_base64(fig)

def figure_to_base64(fig: Figure) -> str:
    """Convert a matplotlib figure to base64 encoded PNG.
    
    Args:
        fig: Matplotlib figure
        
    Returns:
        Base64 encoded PNG image
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('ascii')
    buf.close()
    plt.close(fig)
    return img_str
