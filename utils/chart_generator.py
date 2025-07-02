import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
import plotly.io as pio
from pathlib import Path
import atexit
import signal
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Plotly to use a single Kaleido instance
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_scale = 2

class ChartGenerator:
    """Handles chart generation with proper resource cleanup."""
    
    def __init__(self):
        self._temp_dir = Path('temp_charts')
        self._temp_dir.mkdir(exist_ok=True)
        self._cleanup_registered = False
        self._register_cleanup()
    
    def _register_cleanup(self):
        """Register cleanup handlers for proper resource cleanup."""
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            # Register signal handlers for clean exit
            for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGABRT):
                try:
                    signal.signal(sig, self._signal_handler)
                except (ValueError, RuntimeError) as e:
                    logger.warning(f"Could not register signal handler for {sig}: {e}")
            self._cleanup_registered = True
    
    def _signal_handler(self, signum, frame):
        """Handle signals for clean exit."""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        try:
            if hasattr(pio.kaleido.scope, '_shutdown_kaleido'):
                pio.kaleido.scope._shutdown_kaleido()
        except Exception as e:
            logger.error(f"Error during Kaleido shutdown: {e}")
        
        # Clean up temporary directory
        try:
            if self._temp_dir.exists():
                for file in self._temp_dir.glob('*'):
                    try:
                        if file.is_file():
                            file.unlink()
                    except Exception as e:
                        logger.error(f"Error deleting {file}: {e}")
        except Exception as e:
            logger.error(f"Error during temp directory cleanup: {e}")
    
    def _create_base_figure(self, title: str, **kwargs) -> go.Figure:
        """Create a base figure with consistent styling."""
        fig = go.Figure(**kwargs)
        fig.update_layout(
            title=title,
            plot_bgcolor='white',
            xaxis_showgrid=False,
            yaxis_showgrid=True,
            yaxis_gridcolor='#f0f0f0',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        return fig
    
    def _save_plot(self, fig: go.Figure, filename: str) -> Optional[str]:
        """Save a plot to a temporary file with error handling."""
        try:
            filepath = self._temp_dir / f"{filename}.png"
            
            # Ensure the directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the figure
            fig.write_image(
                filepath,
                format='png',
                engine='kaleido',
                width=1000,
                height=600,
                scale=2
            )
            
            # Verify the file was created and has content
            if not filepath.exists() or filepath.stat().st_size == 0:
                logger.error(f"Failed to create or empty file: {filepath}")
                return None
                
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving plot {filename}: {str(e)}", exc_info=True)
            return None

    def generate_commit_activity_chart(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Generate an enhanced commit activity chart with more details."""
        if not commits:
            return None
            
        try:
            df = pd.DataFrame(commits)
            df['date'] = pd.to_datetime(df['date'])
            
            # Extract date components for grouping
            df['date_day'] = df['date'].dt.date
            df['day_of_week'] = df['date'].dt.day_name()
            df['hour_of_day'] = df['date'].dt.hour
            
            # Group by date and calculate metrics
            daily_stats = df.groupby('date_day').agg({
                'sha': 'count',
                'additions': 'sum',
                'deletions': 'sum',
                'files_changed': lambda x: sum(len(f) for f in x if isinstance(f, list)),
                'author': lambda x: x.nunique()  # Number of unique authors
            }).reset_index()
            
            daily_stats = daily_stats.rename(columns={
                'sha': 'commits',
                'author': 'unique_authors'
            })
            
            if len(daily_stats) < 2:
                return None
                
            # Create figure with secondary y-axis
            fig = go.Figure()
            
            # Add bars for commits
            fig.add_trace(go.Bar(
                x=daily_stats['date_day'],
                y=daily_stats['commits'],
                name='Commits',
                marker_color='#4c78a8',
                text=daily_stats['commits'],
                textposition='auto',
                hoverinfo='text',
                hovertext=[
                    f"<b>{row['date_day']}</b><br>"
                    f"Commits: {row['commits']}<br>"
                    f"Additions: {row['additions']:,}<br>"
                    f"Deletions: {row['deletions']:,}<br>"
                    f"Files Changed: {row['files_changed']:,}<br>"
                    f"Unique Authors: {row['unique_authors']}"
                    for _, row in daily_stats.iterrows()
                ]
            ))
            
            # Add line for 7-day moving average
            if len(daily_stats) > 7:
                daily_stats['moving_avg'] = daily_stats['commits'].rolling(window=7, min_periods=1).mean()
                fig.add_trace(go.Scatter(
                    x=daily_stats['date_day'],
                    y=daily_stats['moving_avg'],
                    name='7-Day Avg',
                    mode='lines',
                    line=dict(color='#ff7f0e', width=3, dash='dot'),
                    yaxis='y2',
                    hoverinfo='y+text',
                    hovertext=['7-day average'] * len(daily_stats)
                ))
            
            # Add heatmap for commit distribution by day of week and hour
            heatmap_data = df.pivot_table(
                index='day_of_week',
                columns='hour_of_day',
                values='sha',
                aggfunc='count',
                fill_value=0
            )
            
            # Reorder days of week
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex(days_order)
            
            # Create heatmap figure
            heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=[f"{h:02d}:00" for h in range(24)],
                y=heatmap_data.index,
                colorscale='Blues',
                showscale=True,
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Commits: %{z}<extra></extra>'
            ))
            
            heatmap.update_layout(
                title='🕒 Commit Distribution by Day & Hour',
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                height=400,
                margin=dict(l=60, r=30, t=60, b=60),
                plot_bgcolor='white'
            )
            
            # Create subplots
            from plotly.subplots import make_subplots
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.6, 0.4],
                subplot_titles=('📅 Daily Commit Activity', '🕒 Commit Distribution by Day & Hour'),
                vertical_spacing=0.15
            )
            
            # Add traces to subplot
            fig.add_trace(go.Bar(
                x=daily_stats['date_day'],
                y=daily_stats['commits'],
                name='Commits',
                marker_color='#4c78a8',
                text=daily_stats['commits'],
                textposition='auto',
                hoverinfo='text',
                hovertext=[
                    f"<b>{row['date_day']}</b><br>"
                    f"Commits: {row['commits']}<br>"
                    f"Additions: {row['additions']:,}<br>"
                    f"Deletions: {row['deletions']:,}<br>"
                    f"Files Changed: {row['files_changed']:,}<br>"
                    f"Unique Authors: {row['unique_authors']}"
                    for _, row in daily_stats.iterrows()
                ]
            ), row=1, col=1)
            
            if 'moving_avg' in daily_stats.columns:
                fig.add_trace(go.Scatter(
                    x=daily_stats['date_day'],
                    y=daily_stats['moving_avg'],
                    name='7-Day Avg',
                    mode='lines',
                    line=dict(color='#ff7f0e', width=3, dash='dot'),
                    hoverinfo='y+text',
                    hovertext=['7-day average'] * len(daily_stats)
                ), row=1, col=1)
            
            # Add heatmap to subplot
            fig.add_trace(go.Heatmap(
                z=heatmap_data.values,
                x=[f"{h:02d}:00" for h in range(24)],
                y=heatmap_data.index,
                colorscale='Blues',
                showscale=True,
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Commits: %{z}<extra></extra>',
                colorbar=dict(
                    title='Commits',
                    thickness=10,
                    yanchor='top',
                    y=0.3,
                    len=0.3
                )
            ), row=2, col=1)
            
            # Update layout
            fig.update_layout(
                height=1000,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=30, t=100, b=60),
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor='white',
                    font_size=12,
                    font_family='Arial'
                ),
                xaxis=dict(
                    title='Date',
                    showgrid=False,
                    tickangle=45
                ),
                yaxis=dict(
                    title='Number of Commits',
                    showgrid=False
                ),
                xaxis2=dict(
                    title='Hour of Day',
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Day of Week',
                    showgrid=False
                )
            )
            
            # Add annotations
            fig.add_annotation(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                text="<i>Hover over points for detailed information</i>",
                showarrow=False,
                font=dict(size=10, color='gray')
            )
            
            return self._save_plot(fig, 'commit_activity')
            
        except Exception as e:
            logger.error(f"Error in generate_commit_activity_chart: {str(e)}", exc_info=True)
            return None

    def generate_author_contribution_chart(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a chart showing contributions by author."""
        if not commits:
            return None
            
        try:
            df = pd.DataFrame(commits)
            if 'author' not in df.columns:
                return None
                
            author_stats = df.groupby('author').size().reset_index(name='commits')
            
            if len(author_stats) == 0:
                return None
                
            # Use a default color sequence instead of px.colors
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            fig = self._create_base_figure(
                title='👥 Commits by Author',
                data=[go.Bar(
                    x=author_stats['author'],
                    y=author_stats['commits'],
                    marker_color=colors[:len(author_stats)]
                )]
            )
            
            fig.update_layout(
                xaxis_title='Author',
                yaxis_title='Number of Commits',
                showlegend=False
            )
            
            return self._save_plot(fig, 'author_contributions')
            
        except Exception as e:
            logger.error(f"Error in generate_author_contribution_chart: {str(e)}", exc_info=True)
            return None

    def generate_file_activity_chart(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a chart showing most active files."""
        if not commits:
            return None
            
        try:
            file_changes = {}
            for commit in commits:
                for file in commit.get('files_changed', []):
                    if isinstance(file, dict) and 'filename' in file:
                        filename = file['filename']
                        file_changes[filename] = file_changes.get(filename, 0) + 1
            
            if not file_changes:
                return None
                
            # Get top 10 most changed files
            top_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10]
            if not top_files:
                return None
                
            df = pd.DataFrame(top_files, columns=['filename', 'changes'])
            
            fig = self._create_base_figure(
                title='📝 Most Active Files',
                data=[go.Bar(
                    x=df['changes'],
                    y=df['filename'],
                    orientation='h',
                    marker_color='#00CC96'
                )]
            )
            
            fig.update_layout(
                xaxis_title='Number of Changes',
                yaxis_title='File',
                yaxis=dict(autorange="reversed")
            )
            
            return self._save_plot(fig, 'file_activity')
            
        except Exception as e:
            logger.error(f"Error in generate_file_activity_chart: {str(e)}")
            return None

    def generate_hourly_commit_chart(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a chart showing commit activity by hour of day."""
        if not commits:
            return None
            
        try:
            df = pd.DataFrame(commits)
            df['hour'] = pd.to_datetime(df['date']).dt.hour
            hourly_commits = df.groupby('hour').size().reset_index(name='count')
            
            if len(hourly_commits) == 0:
                return None
                
            fig = self._create_base_figure(
                title='🕒 Commit Activity by Hour of Day',
                data=[go.Bar(
                    x=hourly_commits['hour'],
                    y=hourly_commits['count'],
                    marker_color='#EF553B'
                )]
            )
            
            fig.update_layout(
                xaxis_title='Hour of Day (24h)',
                yaxis_title='Number of Commits',
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(24)),
                    ticktext=[f"{h:02d}:00" for h in range(24)]
                )
            )
            
            return self._save_plot(fig, 'hourly_commits')
            
        except Exception as e:
            logger.error(f"Error in generate_hourly_commit_chart: {str(e)}")
            return None

    def generate_review_influence_map(self, pull_requests: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a code-review influence map showing relationships between reviewers and authors.
        
        Args:
            pull_requests: List of pull request data with 'author' and 'reviewers' fields
            
        Returns:
            Path to the saved chart image or None if generation fails
        """
        logger.info("Starting review influence map generation...")
        
        if not pull_requests:
            logger.warning("No pull request data provided")
            return None
            
        try:
            logger.info(f"Processing {len(pull_requests)} pull requests")
            
            # Process data to count review relationships
            review_edges = []
            for pr in pull_requests:
                # Get author from commit data if not in PR data
                author = pr.get('author')
                if not author and 'commit' in pr and 'author' in pr['commit']:
                    author = pr['commit']['author'].get('login') or pr['commit']['author'].get('name')
                
                reviewers = pr.get('reviewers', [])
                
                if not author or not reviewers:
                    logger.warning(f"Skipping PR due to missing author or reviewers. Author: {author}, Reviewers: {reviewers}")
                    continue
                    
                logger.debug(f"Processing PR by {author} with {len(reviewers)} reviewers")
                for reviewer in reviewers:
                    if reviewer:  # Skip empty reviewer names
                        review_edges.append({'source': reviewer, 'target': author, 'weight': 1})
            
            if not review_edges:
                logger.warning("No valid review relationships found in pull request data")
                logger.warning(f"Processed {len(pull_requests)} PRs but found no valid author-reviewer pairs")
                return None
                
            logger.info(f"Found {len(review_edges)} review relationships")
            
            # Create DataFrame and group by source/target
            df_edges = pd.DataFrame(review_edges)
            df_edges = df_edges.groupby(['source', 'target'])['weight'].sum().reset_index()
            
            # Get unique authors and reviewers
            authors = set(df_edges['target'].unique())
            reviewers = set(df_edges['source'].unique())
            all_nodes = list(authors.union(reviewers))
            
            logger.info(f"Found {len(authors)} authors and {len(reviewers)} reviewers")
            logger.debug(f"Authors: {authors}")
            logger.debug(f"Reviewers: {reviewers}")
            
            if not all_nodes:
                logger.warning("No valid nodes found for the graph")
                return None
                
            # Create figure
            fig = go.Figure()
            
            # Add edges
            for _, row in df_edges.iterrows():
                try:
                    source_idx = all_nodes.index(row['source'])
                    target_idx = all_nodes.index(row['target'])
                    
                    fig.add_trace(go.Scatter(
                        x=[source_idx, (source_idx + target_idx) / 2, target_idx],
                        y=[0, 0.4, 1],
                        mode='lines',
                        line=dict(width=min(8, 1 + row['weight'] * 0.5), color='rgba(100, 100, 200, 0.4)'),
                        hoverinfo='text',
                        hovertext=f"{row['source']} → {row['target']}<br>Reviews: {row['weight']}",
                        showlegend=False
                    ))
                except Exception as e:
                    logger.error(f"Error adding edge {row['source']} → {row['target']}: {str(e)}")
            
            # Add reviewer nodes (top)
            reviewer_nodes = [node for node in all_nodes if node in reviewers]
            reviewer_x = [all_nodes.index(node) for node in reviewer_nodes]
            
            # Add author nodes (bottom)
            author_nodes = [node for node in all_nodes if node in authors]
            author_x = [all_nodes.index(node) for node in author_nodes]
            
            # Add reviewer nodes trace
            if reviewer_x:
                fig.add_trace(go.Scatter(
                    x=reviewer_x,
                    y=[0] * len(reviewer_nodes),
                    mode='markers+text',
                    marker=dict(size=20, color='#ff7f0e', line=dict(width=2, color='#cc6a00')),
                    text=reviewer_nodes,
                    textposition='top center',
                    name='Reviewers',
                    hoverinfo='text',
                    hovertext=[f'Reviewer: {node}<br>Reviews given: {sum(df_edges[df_edges["source"] == node]["weight"])}' 
                              for node in reviewer_nodes]
                ))
            
            # Add author nodes trace
            if author_x:
                fig.add_trace(go.Scatter(
                    x=author_x,
                    y=[1] * len(author_nodes),
                    mode='markers+text',
                    marker=dict(size=20, color='#1f77b4', line=dict(width=2, color='#15507a')),
                    text=author_nodes,
                    textposition='bottom center',
                    name='Authors',
                    hoverinfo='text',
                    hovertext=[f'Author: {node}<br>Reviews received: {sum(df_edges[df_edges["target"] == node]["weight"])}' 
                              for node in author_nodes]
                ))
            
            # Update layout
            fig.update_layout(
                title='Code Review Influence Map',
                showlegend=True,
                hovermode='closest',
                margin=dict(b=100, l=50, r=50, t=80),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
                plot_bgcolor='white',
                height=600,
                annotations=[
                    dict(text="Reviewers", x=0.5, y=1.05, showarrow=False, 
                         xref="paper", yref="paper", font=dict(size=14, color="#ff7f0e")),
                    dict(text="Authors", x=0.5, y=-0.1, showarrow=False, 
                         xref="paper", yref="paper", font=dict(size=14, color="#1f77b4"))
                ]
            )
            
            # Save the plot
            chart_path = self._save_plot(fig, 'review_influence_map')
            if chart_path and os.path.exists(chart_path):
                logger.info(f"Successfully saved chart to {chart_path}")
                return chart_path
            else:
                logger.error("Failed to save chart")
                return None
                
        except Exception as e:
            logger.error(f"Error in generate_review_influence_map: {str(e)}", exc_info=True)
            return None

def generate_all_charts(commits: List[Dict[str, Any]], pull_requests: List[Dict[str, Any]] = None) -> List[str]:
    """
    Generate all available charts and return their file paths.
    
    Args:
        commits: List of commit data
        pull_requests: Optional list of pull request data for review influence map
        
    Returns:
        List of paths to generated chart images
    """
    if not commits and not pull_requests:
        return []
        
    chart_paths = []
    generator = ChartGenerator()
    
    # Generate commit-based charts if commits are available
    if commits:
        chart_generators = [
            (generator.generate_commit_activity_chart, "commit_activity"),
            (generator.generate_author_contribution_chart, "author_contributions"),
            (generator.generate_file_activity_chart, "file_activity"),
            (generator.generate_hourly_commit_chart, "hourly_commits")
        ]
        
        for generator_func, chart_name in chart_generators:
            try:
                chart_path = generator_func(commits)
                if chart_path and os.path.exists(chart_path):
                    chart_paths.append(chart_path)
                else:
                    logger.warning(f"Failed to generate {chart_name} chart")
            except Exception as e:
                logger.error(f"Error in chart generator {generator_func.__name__}: {str(e)}", exc_info=True)
                continue
    
    # Generate review influence map if pull request data is available
    if pull_requests:
        try:
            chart_path = generator.generate_review_influence_map(pull_requests)
            if chart_path and os.path.exists(chart_path):
                chart_paths.append(chart_path)
            else:
                logger.warning("Failed to generate review influence map")
        except Exception as e:
            logger.error(f"Error generating review influence map: {str(e)}", exc_info=True)
    
    return chart_paths
