"""Diff Analyst Agent - Analyzes code changes and computes DORA metrics."""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics

from .base import BaseAgent, AgentError
from ..data.database import db
from ..data.models import GitHubEvent, DiffStats, DORAMetrics, Metric, EventType, MetricType
from ..graph.state import WorkflowState
from ..config import logger


class DiffAnalystAgent(BaseAgent):
    """Agent responsible for analyzing code changes and computing productivity metrics."""
    
    def __init__(self):
        super().__init__(
            name="DiffAnalyst",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """You are a Diff Analyst Agent specialized in analyzing software engineering productivity metrics.

Your role is to:
1. Analyze code churn patterns and identify anomalies
2. Interpret DORA metrics in context of team performance
3. Detect potential productivity risks and code quality issues
4. Provide insights on engineering efficiency and collaboration patterns

You should focus on:
- Code churn analysis (additions, deletions, file changes)
- Deployment frequency and lead time patterns
- Change failure rate implications
- Developer productivity trends
- Collaboration and review efficiency

Provide actionable insights that help engineering teams improve their productivity and code quality.
Highlight both positive trends and areas for improvement."""
    
    def process(self, state: WorkflowState) -> WorkflowState:
        """Analyze GitHub events and compute productivity metrics."""
        logger.info(f"Starting diff analysis for {len(state['github_events'])} events")
        
        try:
            events = state["github_events"]
            
            if not events:
                error_msg = "No events available for analysis"
                state["errors"].append(error_msg)
                return state
            
            # Compute diff statistics per author
            diff_stats = self._compute_diff_stats(events, state)
            
            # Compute DORA metrics
            dora_metrics = self._compute_dora_metrics(events, state)
            
            # Detect anomalies and risks
            anomalies = self._detect_anomalies(diff_stats, events)
            risk_factors = self._analyze_risk_factors(diff_stats, dora_metrics)
            
            # Store computed metrics in database
            self._store_metrics(diff_stats, dora_metrics, state)
            
            # Generate AI-powered analysis
            analysis_insights = self._generate_analysis_insights(
                diff_stats, dora_metrics, anomalies, risk_factors
            )
            
            # Update state
            state["diff_stats"] = diff_stats
            state["dora_metrics"] = dora_metrics
            state["anomalies"] = anomalies
            state["risk_factors"] = risk_factors
            
            # Store agent-specific data
            state["agent_data"]["diff_analyst"] = {
                "metrics_computed": len(diff_stats),
                "dora_metrics": dora_metrics.dict() if dora_metrics else None,
                "anomalies_detected": len(anomalies),
                "analysis_insights": analysis_insights,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Diff analysis completed: {len(diff_stats)} author stats, {len(anomalies)} anomalies")
            return state
            
        except Exception as e:
            error_msg = f"Diff analysis failed: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            raise AgentError("DiffAnalyst", error_msg, e)
    
    def _compute_diff_stats(self, events: List[GitHubEvent], state: WorkflowState) -> List[DiffStats]:
        """Compute diff statistics per author."""
        author_stats = defaultdict(lambda: {
            'additions': 0,
            'deletions': 0,
            'files_changed': 0,
            'commits': 0,
            'events': []
        })
        
        # Aggregate data by author
        for event in events:
            if event.event_type == EventType.COMMIT:
                stats = author_stats[event.author]
                stats['additions'] += event.additions or 0
                stats['deletions'] += event.deletions or 0
                stats['files_changed'] += event.changed_files or 0
                stats['commits'] += 1
                stats['events'].append(event)
        
        # Compute DiffStats objects
        diff_stats = []
        for author, stats in author_stats.items():
            total_changes = stats['additions'] + stats['deletions']
            churn_rate = total_changes / max(stats['additions'], 1)  # Avoid division by zero
            files_per_commit = stats['files_changed'] / max(stats['commits'], 1)
            
            diff_stat = DiffStats(
                author=author,
                repo_name=state["repo_name"],
                period_start=state["period_start"],
                period_end=state["period_end"],
                total_additions=stats['additions'],
                total_deletions=stats['deletions'],
                total_files_changed=stats['files_changed'],
                commit_count=stats['commits'],
                churn_rate=churn_rate,
                files_per_commit=files_per_commit
            )
            diff_stats.append(diff_stat)
        
        return diff_stats
    
    def _compute_dora_metrics(self, events: List[GitHubEvent], state: WorkflowState) -> Optional[DORAMetrics]:
        """Compute DORA four key metrics."""
        try:
            # Filter events by type
            commits = [e for e in events if e.event_type == EventType.COMMIT]
            prs = [e for e in events if e.event_type == EventType.PULL_REQUEST]
            reviews = [e for e in events if e.event_type == EventType.PULL_REQUEST_REVIEW]
            
            # 1. Lead Time (time from first commit to PR merge)
            lead_times = []
            for pr in prs:
                if pr.raw_data.get('merged_at'):
                    # Find related commits
                    pr_commits = [c for c in commits if c.pr_number == pr.pr_number]
                    if pr_commits:
                        first_commit_time = min(c.timestamp for c in pr_commits)
                        merge_time = datetime.fromisoformat(
                            pr.raw_data['merged_at'].replace('Z', '+00:00')
                        )
                        lead_time_hours = (merge_time - first_commit_time).total_seconds() / 3600
                        lead_times.append(lead_time_hours)
            
            avg_lead_time = statistics.mean(lead_times) if lead_times else None
            
            # 2. Deployment Frequency (PRs merged per day)
            period_days = (state["period_end"] - state["period_start"]).days
            merged_prs = len([pr for pr in prs if pr.raw_data.get('merged_at')])
            deployment_frequency = merged_prs / max(period_days, 1)
            
            # 3. Change Failure Rate (approximate from reverts/fixes)
            fix_keywords = ['fix', 'bug', 'revert', 'hotfix', 'patch']
            fix_commits = [
                c for c in commits 
                if any(keyword in c.raw_data.get('commit', {}).get('message', '').lower() 
                       for keyword in fix_keywords)
            ]
            change_failure_rate = len(fix_commits) / max(len(commits), 1)
            
            # 4. MTTR (time between fix commits - rough approximation)
            mttr_hours = None
            if len(fix_commits) > 1:
                fix_times = [c.timestamp for c in sorted(fix_commits, key=lambda x: x.timestamp)]
                time_diffs = [
                    (fix_times[i] - fix_times[i-1]).total_seconds() / 3600 
                    for i in range(1, len(fix_times))
                ]
                mttr_hours = statistics.mean(time_diffs)
            
            return DORAMetrics(
                repo_name=state["repo_name"],
                period_start=state["period_start"],
                period_end=state["period_end"],
                lead_time_hours=avg_lead_time,
                deployment_frequency=deployment_frequency,
                change_failure_rate=change_failure_rate,
                mttr_hours=mttr_hours
            )
            
        except Exception as e:
            logger.warning(f"Failed to compute DORA metrics: {e}")
            return None
    
    def _detect_anomalies(self, diff_stats: List[DiffStats], events: List[GitHubEvent]) -> List[str]:
        """Detect anomalies in code churn and activity patterns."""
        anomalies = []
        
        if not diff_stats:
            return anomalies
        
        # Analyze churn rates
        churn_rates = [stat.churn_rate for stat in diff_stats]
        if churn_rates:
            avg_churn = statistics.mean(churn_rates)
            max_churn = max(churn_rates)
            
            # High churn anomaly
            if max_churn > avg_churn * 3:
                high_churn_author = next(s.author for s in diff_stats if s.churn_rate == max_churn)
                anomalies.append(f"High code churn detected for {high_churn_author} (rate: {max_churn:.2f})")
        
        # Large commit anomaly
        large_commits = [
            stat for stat in diff_stats 
            if stat.total_additions + stat.total_deletions > 1000
        ]
        for stat in large_commits:
            anomalies.append(f"Large commit volume for {stat.author} ({stat.total_additions + stat.total_deletions} lines changed)")
        
        # Low activity anomaly
        low_activity = [stat for stat in diff_stats if stat.commit_count == 1]
        if len(low_activity) > len(diff_stats) * 0.5:
            anomalies.append("High proportion of authors with minimal activity")
        
        # File churn anomaly
        high_file_churn = [stat for stat in diff_stats if stat.files_per_commit > 10]
        for stat in high_file_churn:
            anomalies.append(f"High file churn for {stat.author} ({stat.files_per_commit:.1f} files per commit)")
        
        return anomalies
    
    def _analyze_risk_factors(self, diff_stats: List[DiffStats], dora_metrics: Optional[DORAMetrics]) -> List[str]:
        """Analyze potential risk factors for code quality and productivity."""
        risks = []
        
        # High change failure rate
        if dora_metrics and dora_metrics.change_failure_rate and dora_metrics.change_failure_rate > 0.15:
            risks.append(f"High change failure rate ({dora_metrics.change_failure_rate:.1%}) indicates potential quality issues")
        
        # Long lead times
        if dora_metrics and dora_metrics.lead_time_hours and dora_metrics.lead_time_hours > 168:  # > 1 week
            risks.append(f"Long lead times ({dora_metrics.lead_time_hours:.1f} hours) may indicate process bottlenecks")
        
        # Low deployment frequency
        if dora_metrics and dora_metrics.deployment_frequency and dora_metrics.deployment_frequency < 0.2:  # < 1 per 5 days
            risks.append("Low deployment frequency may indicate slow delivery pipeline")
        
        # Code concentration risk
        if diff_stats:
            total_changes = sum(s.total_additions + s.total_deletions for s in diff_stats)
            max_author_changes = max(s.total_additions + s.total_deletions for s in diff_stats)
            
            if max_author_changes / total_changes > 0.6:  # One author > 60% of changes
                dominant_author = next(
                    s.author for s in diff_stats 
                    if s.total_additions + s.total_deletions == max_author_changes
                )
                risks.append(f"High code concentration risk - {dominant_author} responsible for {max_author_changes/total_changes:.1%} of changes")
        
        return risks
    
    def _store_metrics(self, diff_stats: List[DiffStats], dora_metrics: Optional[DORAMetrics], state: WorkflowState):
        """Store computed metrics in the database."""
        timestamp = datetime.now()
        
        # Store diff stats as individual metrics
        for stat in diff_stats:
            metrics = [
                Metric(
                    repo_name=stat.repo_name,
                    author=stat.author,
                    metric_type=MetricType.COMMIT_COUNT,
                    value=stat.commit_count,
                    period="custom",
                    timestamp=timestamp
                ),
                Metric(
                    repo_name=stat.repo_name,
                    author=stat.author,
                    metric_type=MetricType.LINES_ADDED,
                    value=stat.total_additions,
                    period="custom",
                    timestamp=timestamp
                ),
                Metric(
                    repo_name=stat.repo_name,
                    author=stat.author,
                    metric_type=MetricType.LINES_DELETED,
                    value=stat.total_deletions,
                    period="custom",
                    timestamp=timestamp
                ),
                Metric(
                    repo_name=stat.repo_name,
                    author=stat.author,
                    metric_type=MetricType.FILES_CHANGED,
                    value=stat.total_files_changed,
                    period="custom",
                    timestamp=timestamp
                )
            ]
            
            for metric in metrics:
                db.insert_metric(metric)
        
        # Store DORA metrics
        if dora_metrics:
            dora_metric_list = []
            
            if dora_metrics.lead_time_hours is not None:
                dora_metric_list.append(Metric(
                    repo_name=dora_metrics.repo_name,
                    author="team",
                    metric_type=MetricType.LEAD_TIME,
                    value=dora_metrics.lead_time_hours,
                    period="custom",
                    timestamp=timestamp
                ))
            
            if dora_metrics.deployment_frequency is not None:
                dora_metric_list.append(Metric(
                    repo_name=dora_metrics.repo_name,
                    author="team",
                    metric_type=MetricType.DEPLOYMENT_FREQUENCY,
                    value=dora_metrics.deployment_frequency,
                    period="custom",
                    timestamp=timestamp
                ))
            
            for metric in dora_metric_list:
                db.insert_metric(metric)
    
    def _generate_analysis_insights(
        self,
        diff_stats: List[DiffStats],
        dora_metrics: Optional[DORAMetrics],
        anomalies: List[str],
        risk_factors: List[str]
    ) -> str:
        """Generate AI-powered insights from the analysis."""
        
        context = {
            "author_count": len(diff_stats),
            "total_commits": sum(s.commit_count for s in diff_stats),
            "total_changes": sum(s.total_additions + s.total_deletions for s in diff_stats),
            "dora_metrics": dora_metrics.dict() if dora_metrics else "Not available",
            "anomalies": anomalies[:5],  # Limit to top 5 anomalies
            "risk_factors": risk_factors[:5],  # Limit to top 5 risks
            "top_contributors": [
                {"author": s.author, "commits": s.commit_count, "changes": s.total_additions + s.total_deletions}
                for s in sorted(diff_stats, key=lambda x: x.commit_count, reverse=True)[:3]
            ]
        }
        
        prompt = """Analyze this repository's productivity metrics:

Team Activity:
- {author_count} contributors
- {total_commits} total commits  
- {total_changes} total line changes

DORA Metrics: {dora_metrics}

Top Contributors: {top_contributors}

Detected Anomalies: {anomalies}

Risk Factors: {risk_factors}

Provide a concise analysis focusing on:
1. Overall team productivity assessment
2. Key patterns or concerns in the data
3. Most significant findings that leadership should know

Keep response under 200 words and focus on actionable insights."""
        
        try:
            insights = self._invoke_llm(prompt, context)
            return insights.strip()
        except Exception as e:
            logger.warning(f"Failed to generate analysis insights: {e}")
            return f"Analysis completed for {len(diff_stats)} contributors with {sum(s.commit_count for s in diff_stats)} total commits."


# Global instance
diff_analyst = DiffAnalystAgent()