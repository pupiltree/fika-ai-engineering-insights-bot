"""Chart generation for productivity visualizations."""
import io
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ..data.models import DiffStats, DORAMetrics, GitHubEvent
from ..config import settings, logger


class ProductivityCharts:
    """Generate charts for productivity analysis."""
    
    def __init__(self):
        self.chart_dir = Path("data/charts")
        self.chart_dir.mkdir(parents=True, exist_ok=True)
        
        # Set chart styling
        plt.style.use('default')
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#8B5A3C']
    
    def generate_commit_activity_chart(
        self, 
        events: List[GitHubEvent], 
        title: str = "Commit Activity Over Time"
    ) -> str:
        """Generate commit activity timeline chart."""
        try:
            # Filter commit events
            commits = [e for e in events if e.event_type.value == "commit"]
            
            if not commits:
                return self._create_no_data_chart(title)
            
            # Prepare data
            dates = [c.timestamp.date() for c in commits]
            df = pd.DataFrame({'date': dates})
            daily_counts = df.groupby('date').size().reset_index(name='commits')
            
            # Create Plotly chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_counts['date'],
                y=daily_counts['commits'],
                mode='lines+markers',
                name='Daily Commits',
                line=dict(color=self.colors[0], width=3),
                marker=dict(size=8, color=self.colors[0])
            ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title="Date",
                yaxis_title="Number of Commits",
                template="plotly_white",
                width=settings.chart_width,
                height=settings.chart_height,
                showlegend=False
            )
            
            # Save chart
            filename = f"commit_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.chart_dir / filename
            fig.write_image(str(filepath))
            
            logger.info(f"Generated commit activity chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate commit activity chart: {e}")
            return self._create_error_chart(title, str(e))
    
    def generate_contributor_comparison_chart(
        self, 
        diff_stats: List[DiffStats],
        title: str = "Contributor Productivity Comparison"
    ) -> str:
        """Generate bar chart comparing contributor productivity."""
        try:
            if not diff_stats:
                return self._create_no_data_chart(title)
            
            # Sort by commit count
            sorted_stats = sorted(diff_stats, key=lambda s: s.commit_count, reverse=True)
            top_contributors = sorted_stats[:10]  # Top 10
            
            authors = [s.author for s in top_contributors]
            commits = [s.commit_count for s in top_contributors]
            changes = [s.total_additions + s.total_deletions for s in top_contributors]
            
            # Create subplot with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add commits bar
            fig.add_trace(
                go.Bar(
                    x=authors,
                    y=commits,
                    name="Commits",
                    marker_color=self.colors[0],
                    yaxis="y"
                ),
                secondary_y=False
            )
            
            # Add lines changed bar
            fig.add_trace(
                go.Bar(
                    x=authors,
                    y=changes,
                    name="Lines Changed",
                    marker_color=self.colors[1],
                    yaxis="y2",
                    opacity=0.7
                ),
                secondary_y=True
            )
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                template="plotly_white",
                width=settings.chart_width,
                height=settings.chart_height,
                barmode='group'
            )
            
            fig.update_xaxes(title_text="Contributors")
            fig.update_yaxes(title_text="Number of Commits", secondary_y=False)
            fig.update_yaxes(title_text="Lines Changed", secondary_y=True)
            
            # Save chart
            filename = f"contributor_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.chart_dir / filename
            fig.write_image(str(filepath))
            
            logger.info(f"Generated contributor comparison chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate contributor comparison chart: {e}")
            return self._create_error_chart(title, str(e))
    
    def generate_dora_metrics_chart(
        self, 
        dora_metrics: DORAMetrics,
        title: str = "DORA Four Key Metrics"
    ) -> str:
        """Generate DORA metrics visualization."""
        try:
            if not dora_metrics:
                return self._create_no_data_chart(title)
            
            # Prepare metrics data
            metrics = []
            values = []
            colors = []
            
            if dora_metrics.lead_time_hours is not None:
                metrics.append("Lead Time (hours)")
                values.append(dora_metrics.lead_time_hours)
                colors.append(self.colors[0])
            
            if dora_metrics.deployment_frequency is not None:
                metrics.append("Deploy Freq (/day)")
                values.append(dora_metrics.deployment_frequency)
                colors.append(self.colors[1])
            
            if dora_metrics.change_failure_rate is not None:
                metrics.append("Failure Rate (%)")
                values.append(dora_metrics.change_failure_rate * 100)
                colors.append(self.colors[2])
            
            if dora_metrics.mttr_hours is not None:
                metrics.append("MTTR (hours)")
                values.append(dora_metrics.mttr_hours)
                colors.append(self.colors[3])
            
            if not metrics:
                return self._create_no_data_chart(title)
            
            # Create horizontal bar chart
            fig = go.Figure(go.Bar(
                x=values,
                y=metrics,
                orientation='h',
                marker_color=colors,
                text=[f"{v:.2f}" for v in values],
                textposition='auto'
            ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title="Value",
                template="plotly_white",
                width=settings.chart_width,
                height=settings.chart_height,
                showlegend=False
            )
            
            # Save chart
            filename = f"dora_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.chart_dir / filename
            fig.write_image(str(filepath))
            
            logger.info(f"Generated DORA metrics chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate DORA metrics chart: {e}")
            return self._create_error_chart(title, str(e))
    
    def generate_code_churn_chart(
        self, 
        diff_stats: List[DiffStats],
        title: str = "Code Churn Analysis"
    ) -> str:
        """Generate code churn visualization."""
        try:
            if not diff_stats:
                return self._create_no_data_chart(title)
            
            authors = [s.author for s in diff_stats]
            additions = [s.total_additions for s in diff_stats]
            deletions = [s.total_deletions for s in diff_stats]
            
            # Create stacked bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=authors,
                y=additions,
                name='Additions',
                marker_color=self.colors[0]
            ))
            
            fig.add_trace(go.Bar(
                x=authors,
                y=[-d for d in deletions],  # Negative for deletions
                name='Deletions',
                marker_color=self.colors[2]
            ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title="Contributors",
                yaxis_title="Lines of Code",
                template="plotly_white",
                width=settings.chart_width,
                height=settings.chart_height,
                barmode='relative'
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Save chart
            filename = f"code_churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.chart_dir / filename
            fig.write_image(str(filepath))
            
            logger.info(f"Generated code churn chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate code churn chart: {e}")
            return self._create_error_chart(title, str(e))
    
    def generate_summary_dashboard(
        self,
        events: List[GitHubEvent],
        diff_stats: List[DiffStats],
        dora_metrics: Optional[DORAMetrics] = None,
        title: str = "Productivity Dashboard"
    ) -> str:
        """Generate comprehensive dashboard with multiple metrics."""
        try:
            # Create subplot grid
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Daily Commits', 'Top Contributors', 'Code Churn', 'DORA Metrics'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 1. Daily commits timeline
            commits = [e for e in events if e.event_type.value == "commit"]
            if commits:
                dates = [c.timestamp.date() for c in commits]
                df = pd.DataFrame({'date': dates})
                daily_counts = df.groupby('date').size().reset_index(name='commits')
                
                fig.add_trace(
                    go.Scatter(
                        x=daily_counts['date'],
                        y=daily_counts['commits'],
                        mode='lines+markers',
                        name='Daily Commits',
                        line=dict(color=self.colors[0])
                    ),
                    row=1, col=1
                )
            
            # 2. Top contributors
            if diff_stats:
                top_5 = sorted(diff_stats, key=lambda s: s.commit_count, reverse=True)[:5]
                fig.add_trace(
                    go.Bar(
                        x=[s.author for s in top_5],
                        y=[s.commit_count for s in top_5],
                        name='Commits',
                        marker_color=self.colors[1]
                    ),
                    row=1, col=2
                )
            
            # 3. Code churn
            if diff_stats:
                fig.add_trace(
                    go.Bar(
                        x=[s.author for s in diff_stats],
                        y=[s.total_additions for s in diff_stats],
                        name='Additions',
                        marker_color=self.colors[0]
                    ),
                    row=2, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=[s.author for s in diff_stats],
                        y=[-s.total_deletions for s in diff_stats],
                        name='Deletions',
                        marker_color=self.colors[2]
                    ),
                    row=2, col=1
                )
            
            # 4. DORA metrics
            if dora_metrics:
                metrics = []
                values = []
                
                if dora_metrics.lead_time_hours:
                    metrics.append("Lead Time")
                    values.append(dora_metrics.lead_time_hours)
                
                if dora_metrics.deployment_frequency:
                    metrics.append("Deploy Freq")
                    values.append(dora_metrics.deployment_frequency)
                
                if metrics:
                    fig.add_trace(
                        go.Bar(
                            x=metrics,
                            y=values,
                            name='DORA',
                            marker_color=self.colors[3]
                        ),
                        row=2, col=2
                    )
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=18)),
                template="plotly_white",
                width=settings.chart_width * 1.5,
                height=settings.chart_height * 1.2,
                showlegend=False
            )
            
            # Save chart
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.chart_dir / filename
            fig.write_image(str(filepath))
            
            logger.info(f"Generated summary dashboard: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate summary dashboard: {e}")
            return self._create_error_chart(title, str(e))
    
    def _create_no_data_chart(self, title: str) -> str:
        """Create a placeholder chart when no data is available."""
        fig = go.Figure()
        
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            title=dict(text=title, x=0.5),
            template="plotly_white",
            width=settings.chart_width,
            height=settings.chart_height,
            showlegend=False
        )
        
        filename = f"no_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.chart_dir / filename
        fig.write_image(str(filepath))
        
        return str(filepath)
    
    def _create_error_chart(self, title: str, error: str) -> str:
        """Create an error chart when visualization fails."""
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"Chart generation failed:\n{error}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=14, color="red")
        )
        
        fig.update_layout(
            title=dict(text=title, x=0.5),
            template="plotly_white",
            width=settings.chart_width,
            height=settings.chart_height,
            showlegend=False
        )
        
        filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.chart_dir / filename
        fig.write_image(str(filepath))
        
        return str(filepath)
    
    def cleanup_old_charts(self, max_age_hours: int = 24):
        """Clean up old chart files to save disk space."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for chart_file in self.chart_dir.glob("*.png"):
                if chart_file.stat().st_mtime < cutoff_time.timestamp():
                    chart_file.unlink()
                    logger.info(f"Cleaned up old chart: {chart_file}")
                    
        except Exception as e:
            logger.warning(f"Failed to clean up old charts: {e}")


# Global charts instance
productivity_charts = ProductivityCharts()