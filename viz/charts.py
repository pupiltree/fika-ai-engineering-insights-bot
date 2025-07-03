import os
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .chart_config import ChartConfig

class ChartGenerationError(Exception):
    pass

def plot_commits_over_time(commits, config: ChartConfig, freq="W", suffix=None):
    try:
        if not commits:
            raise ChartGenerationError("No commit data provided.")
        df = pd.DataFrame(commits)
        df['date'] = pd.to_datetime(df['date'])
        df['period'] = df['date'].dt.to_period(freq).dt.start_time
        grouped = df.groupby(['period', 'author']).size().unstack(fill_value=0)
        plt.figure(figsize=config.figure_size)
        grouped.plot(kind='bar', stacked=True, ax=plt.gca(), color=config.colors)
        plt.title(f"Commits Over Time ({'Weekly' if freq=='W' else 'Daily'}) by Author")
        plt.xlabel("Date")
        plt.ylabel("Number of Commits")
        plt.tight_layout()
        os.makedirs(config.output_dir, exist_ok=True)
        output_path = os.path.join(config.output_dir, f"commits_over_time.png")
        plt.savefig(output_path)
        plt.close()
        return output_path
    except Exception as e:
        print(f"Commits over time chart error: {e}")
        return None

def plot_risky_vs_safe(commits, config: ChartConfig, suffix=None):
    try:
        if not commits:
            raise ChartGenerationError("No commit data provided.")
        risky = sum(1 for c in commits if c.get('is_risky'))
        safe = len(commits) - risky
        labels = ['Risky', 'Safe']
        sizes = [risky, safe]
        colors = config.colors[:2]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Risky vs Safe Commits')
        plt.tight_layout()
        os.makedirs(config.output_dir, exist_ok=True)
        output_path = os.path.join(config.output_dir, f"risky_vs_safe.png")
        plt.savefig(output_path)
        plt.close()
        return output_path
    except Exception as e:
        print(f"Risky vs Safe chart error: {e}")
        return None
    
def create_churn_chart(author_metrics: dict, config: ChartConfig, suffix=None) -> str:
    """Create code churn and commit count visualization by author."""
    try:
        if not author_metrics:
            return None

        authors = list(author_metrics.keys())
        churns = [stats.get('total_churn', 0) for stats in author_metrics.values()]
        commits = [stats.get('commits', 0) for stats in author_metrics.values()]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=config.figure_size)

        # Code churn bar chart
        bars1 = ax1.bar(authors, churns, color=config.colors[0], edgecolor='black')
        ax1.set_title('Code Churn by Author', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Authors')
        ax1.set_ylabel('Lines Changed')
        ax1.tick_params(axis='x', rotation=45)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height + 1,
                     f'{int(height)}', ha='center', va='bottom', fontsize=9)

        # Commit count bar chart
        bars2 = ax2.bar(authors, commits, color=config.colors[1], edgecolor='black')
        ax2.set_title('Commits by Author', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Authors')
        ax2.set_ylabel('Number of Commits')
        ax2.tick_params(axis='x', rotation=45)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, height + 1,
                     f'{int(height)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        chart_path = os.path.join(config.output_dir, f'churn_analysis.png')
        plt.savefig(chart_path, dpi=config.output_settings['dpi'])
        plt.close()
        return chart_path
    except Exception as e:
        print(f"Churn chart error: {e}")
        return None


def create_dora_chart(dora_metrics: dict, config: ChartConfig, suffix=None) -> str:
    """Create a DORA metrics bar chart using ChartConfig for targets and styling."""
    try:
        if not dora_metrics:
            print("No DORA metrics provided.")
            return None

        # Use metric names and keys from config
        metric_keys = list(config.dora_targets.keys())  # ['lead_time', 'deploy_frequency', 'change_failure_rate', 'mttr']
        metric_labels = config.dora_metrics
        targets = [config.dora_targets.get(key, 0) for key in metric_keys]
        values = [dora_metrics.get(key, 0) for key in metric_keys]

        # Use provided colors (or fallback to simple colors if needed)
        bar_colors = config.colors[:len(values)]

        # Create the figure
        fig, ax = plt.subplots(figsize=config.figure_size)

        # Create bars
        bars = ax.bar(metric_labels, values, color=bar_colors, edgecolor='black')

        # Add target lines and annotations
        max_value = max(max(values), max(targets))
        for i, target in enumerate(targets):
            ax.axhline(y=target,
                       xmin=i / len(bars) + 0.1 / len(bars),
                       xmax=(i + 1) / len(bars) - 0.1 / len(bars),
                       color='red', linestyle='--', alpha=0.7)
            ax.text(i, target + max_value * 0.05,
                    f'Target: {target}',
                    ha='center', va='bottom', fontsize=9, color='red')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + max_value * 0.02,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        # Title & styling
        ax.set_title('DORA Four Key Metrics', fontsize=16, fontweight='bold')
        ax.set_ylabel('Values')
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, max_value * 1.3)

        # Save the chart
        os.makedirs(config.output_dir, exist_ok=True)
        chart_path = os.path.join(config.output_dir, f'dora_metrics.png')
        plt.tight_layout()
        plt.savefig(chart_path, **config.output_settings)
        plt.close()

        return chart_path

    except Exception as e:
        print(f"DORA chart error: {e}")
        return None
def create_pr_latency_chart(prs: list, config: ChartConfig, orientation: str = 'vertical', suffix=None) -> str:
    """Create improved PR review latency visualization with modern styling
    
    Args:
        prs: List of PR data
        config: Chart configuration object
        orientation: 'vertical' or 'horizontal' chart orientation
    """
    try:
        if not prs:
            return None
        
        latencies = [pr.get('review_latency_hrs', 0) for pr in prs if pr.get('review_latency_hrs') is not None]
        if not latencies:
            return None
        
        bins = config.pr_latency_bins
        labels = config.pr_latency_labels
        colors = config.pr_latency_colors
        
        # Adjust figure size based on orientation
        if orientation.lower() == 'horizontal':
            fig, ax = plt.subplots(figsize=(config.figure_size[1], config.figure_size[0]))
        else:
            fig, ax = plt.subplots(figsize=config.figure_size)
        
        # Create histogram without colors first (matplotlib doesn't support multiple colors for single dataset)
        counts, bin_edges, bars = ax.hist(
            latencies,
            bins=bins,
            edgecolor='white',
            linewidth=2,
            alpha=0.85,
            orientation='horizontal' if orientation.lower() == 'horizontal' else 'vertical'
        )
        
        # Now apply the colors from config.pr_latency_colors to each individual bar
        for i, bar in enumerate(bars):
            if i < len(config.pr_latency_colors):
                bar.set_facecolor(config.pr_latency_colors[i])
            else:
                # Fallback: cycle through colors if we have more bars than defined colors
                bar.set_facecolor(config.pr_latency_colors[i % len(config.pr_latency_colors)])
        
        # Set title and labels based on orientation
        ax.set_title('PR Review Latency Distribution', fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
        
        if orientation.lower() == 'horizontal':
            ax.set_ylabel('Review Latency', fontsize=14, fontweight='semibold', color='#34495E')
            ax.set_xlabel('Number of PRs', fontsize=14, fontweight='semibold', color='#34495E')
        else:
            ax.set_xlabel('Review Latency', fontsize=14, fontweight='semibold', color='#34495E')
            ax.set_ylabel('Number of PRs', fontsize=14, fontweight='semibold', color='#34495E')
        
        # Set tick labels and rotation based on orientation
        bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(labels))]
        
        if orientation.lower() == 'horizontal':
            label_rotation = 0  # No rotation needed for horizontal bars
            ax.set_yticks(bin_centers)
            ax.set_yticklabels(labels, rotation=label_rotation, fontsize=11, color='#34495E', ha='right')
            ax.tick_params(axis='both', which='major', labelsize=11, colors='#34495E')
            ax.tick_params(axis='y', which='major', pad=10)
        else:
            label_rotation = 90 if len(labels) > 5 else 0
            ax.set_xticks(bin_centers)
            ax.set_xticklabels(labels, rotation=label_rotation, fontsize=11, color='#34495E', 
                              ha='right' if label_rotation > 0 else 'center')
            ax.tick_params(axis='both', which='major', labelsize=11, colors='#34495E')
            ax.tick_params(axis='x', which='major', pad=10)
        
        # Add count and percentage labels on bars
        max_count = max(counts) if len(counts) > 0 else 0
        label_offset = max_count * 0.03
        
        for i, (count, bar) in enumerate(zip(counts, bars)):
            if orientation.lower() == 'horizontal':
                width = bar.get_width()
                height = bar.get_height()
                bar_center_x = bar.get_x() + width / 2
                bar_center_y = bar.get_y() + height / 2
                
                if width > 0:
                    percentage = (count / len(latencies)) * 100
                    
                    # Label positioning for horizontal bars
                    if width > max_count * 0.05:
                        ax.text(width + label_offset, bar_center_y, f'{int(count)}', 
                               ha='left', va='center', fontsize=10, fontweight='bold', color='#2C3E50')
                    
                    if width > max_count * 0.15:
                        ax.text(width / 2, bar_center_y, f'{percentage:.1f}%', 
                               ha='center', va='center', fontsize=9, fontweight='bold', color='white',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
                    else:
                        ax.text(width + label_offset, bar_center_y, f'{int(count)} ({percentage:.1f}%)', 
                               ha='left', va='center', fontsize=9, fontweight='bold', color='#2C3E50',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#BDC3C7'))
            else:
                # Vertical orientation (original logic)
                height = bar.get_height()
                if height > 0:
                    percentage = (count / len(latencies)) * 100
                    bar_width = bar.get_width()
                    bar_center = bar.get_x() + bar_width / 2
                    
                    if height > max_count * 0.05:
                        ax.text(bar_center, height + label_offset, f'{int(count)}', 
                               ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2C3E50')
                    
                    if height > max_count * 0.15:
                        ax.text(bar_center, height / 2, f'{percentage:.1f}%', 
                               ha='center', va='center', fontsize=9, fontweight='bold', color='white',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
                    else:
                        ax.text(bar_center, height + label_offset, f'{int(count)} ({percentage:.1f}%)', 
                               ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2C3E50',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#BDC3C7'))
        
        # Add grid based on orientation
        if orientation.lower() == 'horizontal':
            ax.grid(axis='x', linestyle='--', alpha=0.3, color='#BDC3C7')
        else:
            ax.grid(axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
        
        ax.set_axisbelow(True)
        
        # Add statistics text box
        stats_text = f"""Summary Statistics:\nTotal PRs: {len(latencies)}\nMedian: {np.median(latencies):.1f}h\nMean: {np.mean(latencies):.1f}h\n90th percentile: {np.percentile(latencies, 90):.1f}h"""
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top', 
                horizontalalignment='right', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ECF0F1', 
                alpha=0.9, edgecolor='#BDC3C7'), fontsize=10, color='#2C3E50')
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Set axis limits based on orientation
        if orientation.lower() == 'horizontal':
            ax.set_xlim(left=0)
        else:
            ax.set_ylim(bottom=0)
        
        ax.set_facecolor('#FAFAFA')
        plt.tight_layout(pad=2.0)
        
        chart_filename = 'pr_review.png'
        chart_path = os.path.join(config.output_dir, chart_filename)
        plt.savefig(chart_path, dpi=config.output_settings['dpi'], 
                   bbox_inches=config.output_settings['bbox_inches'], 
                   facecolor=config.output_settings['facecolor'], 
                   edgecolor=config.output_settings['edgecolor'])
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"PR review latency chart error: {e}")
        return None
def create_risk_chart(risk_assessment: dict, config: ChartConfig, suffix=None) -> str:
    try:
        if not risk_assessment:
            return None
        high_risk = len(risk_assessment.get('high_risk_commits', []))
        medium_risk = len(risk_assessment.get('medium_risk_commits', []))
        total_risky = risk_assessment.get('total_risky_commits', 0)
        low_risk = max(0, total_risky - high_risk - medium_risk)
        if total_risky == 0:
            return None
        labels = ['High Risk', 'Medium Risk', 'Low Risk']
        sizes = [high_risk, medium_risk, low_risk]
        colors = config.colors[2:5]
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        if not filtered_data:
            return None
        labels, sizes, colors = zip(*filtered_data)
        fig, ax = plt.subplots(figsize=config.figure_size)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
        ax.set_title('Commit Risk Assessment', fontsize=16, fontweight='bold')
        plt.tight_layout()
        suffix_str = f"_{suffix}" if suffix else ""
        chart_path = os.path.join(config.output_dir, f'risk_assessment{suffix_str}.png')
        plt.savefig(chart_path, dpi=config.output_settings['dpi'], bbox_inches=config.output_settings['bbox_inches'])
        plt.close()
        return chart_path
    except Exception as e:
        print(f"Risk chart error: {e}")
        return None

def create_comprehensive_charts(workflow_result: dict, config: ChartConfig) -> list:
    """Create multiple charts from workflow results using ChartConfig"""
    chart_paths = []
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    insights = workflow_result.get('insights', {})
    analysis_data = workflow_result.get('analysis_data', {})
    github_data = workflow_result.get('github_data', {})

    # 1. Code Churn Chart
    churn_chart = create_churn_chart(analysis_data.get('author_metrics', {}), config)
    if churn_chart:
        chart_paths.append(churn_chart)

    # 2. DORA Metrics Chart
    dora_chart = create_dora_chart(insights.get('dora_metrics', {}), config)
    if dora_chart:
        chart_paths.append(dora_chart)

    # 3. PR Review Latency Chart
    pr_latency_chart = create_pr_latency_chart(github_data.get('prs', []), config)
    if pr_latency_chart:
        chart_paths.append(pr_latency_chart)

    # 4. Risk Assessment Chart
    risk_chart = create_risk_chart(analysis_data.get('risk_assessment', {}), config)
    if risk_chart:
        chart_paths.append(risk_chart)

    return chart_paths
