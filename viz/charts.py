import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

def create_comprehensive_charts(workflow_result: dict) -> list:
    """Create multiple charts from workflow results"""
    chart_paths = []
    
    insights = workflow_result.get('insights', {})
    analysis_data = workflow_result.get('analysis_data', {})
    github_data = workflow_result.get('github_data', {})
    
    # 1. Code Churn Chart
    churn_chart = create_churn_chart(analysis_data.get('author_metrics', {}))
    if churn_chart:
        chart_paths.append(churn_chart)
    
    # 2. DORA Metrics Chart
    dora_chart = create_dora_chart(insights.get('dora_metrics', {}))
    if dora_chart:
        chart_paths.append(dora_chart)
    
    # 3. Risk Assessment Chart
    risk_chart = create_risk_chart(analysis_data.get('risk_assessment', {}))
    if risk_chart:
        chart_paths.append(risk_chart)
    
    return chart_paths

def create_churn_chart(author_metrics: dict) -> str:
    """Create code churn visualization"""
    try:
        if not author_metrics:
            return None
        
        authors = list(author_metrics.keys())
        churns = [stats['total_churn'] for stats in author_metrics.values()]
        commits = [stats['commits'] for stats in author_metrics.values()]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Churn by author
        bars1 = ax1.bar(authors, churns, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax1.set_title('Code Churn by Author', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Authors')
        ax1.set_ylabel('Lines Changed')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Commits by author
        bars2 = ax2.bar(authors, commits, color=['#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'])
        ax2.set_title('Commits by Author', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Authors')
        ax2.set_ylabel('Number of Commits')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        chart_path = 'churn_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"Churn chart error: {e}")
        return None

def create_dora_chart(dora_metrics: dict) -> str:
    """Create DORA metrics visualization"""
    try:
        if not dora_metrics:
            return None
        
        metrics = ['Lead Time\n(hours)', 'Deploy Freq\n(per week)', 
                  'Change Failure\n(%)', 'MTTR\n(hours)']
        values = [dora_metrics.get('lead_time', 0),
                 dora_metrics.get('deploy_frequency', 0),
                 dora_metrics.get('change_failure_rate', 0),
                 dora_metrics.get('mttr', 0)]
        
        # Define target ranges (good performance)
        targets = [24, 5, 10, 2]  # Target values for each metric
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bars
        bars = ax.bar(metrics, values, color=['#2ECC71', '#3498DB', '#E74C3C', '#F39C12'])
        
        # Add target lines
        for i, (bar, target) in enumerate(zip(bars, targets)):
            ax.axhline(y=target, xmin=i/len(bars) + 0.1/len(bars), 
                      xmax=(i+1)/len(bars) - 0.1/len(bars), 
                      color='red', linestyle='--', alpha=0.7)
            ax.text(i, target + max(values) * 0.05, f'Target: {target}', 
                   ha='center', va='bottom', fontsize=9, color='red')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('DORA Four Key Metrics', fontsize=16, fontweight='bold')
        ax.set_ylabel('Values')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        chart_path = 'dora_metrics.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"DORA chart error: {e}")
        return None

def create_risk_chart(risk_assessment: dict) -> str:
    """Create risk assessment visualization"""
    try:
        if not risk_assessment:
            return None
        
        high_risk = len(risk_assessment.get('high_risk_commits', []))
        medium_risk = len(risk_assessment.get('medium_risk_commits', []))
        total_risky = risk_assessment.get('total_risky_commits', 0)
        low_risk = max(0, total_risky - high_risk - medium_risk)
        
        if total_risky == 0:
            return None
        
        # Pie chart
        labels = ['High Risk', 'Medium Risk', 'Low Risk']
        sizes = [high_risk, medium_risk, low_risk]
        colors = ['#E74C3C', '#F39C12', '#2ECC71']
        
        # Filter out zero values
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        if not filtered_data:
            return None
        
        labels, sizes, colors = zip(*filtered_data)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 12})
        
        ax.set_title('Commit Risk Assessment', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        chart_path = 'risk_assessment.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"Risk chart error: {e}")
        return None
