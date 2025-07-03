"""Insight Narrator Agent - Transforms analysis into compelling narratives."""
from datetime import datetime
from typing import List, Dict, Any, Optional

from .base import BaseAgent, AgentError
from ..data.models import DiffStats, DORAMetrics
from ..graph.state import WorkflowState
from ..viz.charts import productivity_charts
from ..config import logger


class InsightNarratorAgent(BaseAgent):
    """Agent responsible for creating compelling narratives from productivity analysis."""
    
    def __init__(self):
        super().__init__(
            name="InsightNarrator",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """You are an Insight Narrator Agent specialized in transforming engineering productivity data into compelling, actionable narratives for engineering leadership.

Your role is to:
1. Create executive-level summaries that highlight key insights
2. Tell the story behind the data in a way that drives action
3. Focus on business impact and team dynamics
4. Provide clear, specific recommendations
5. Balance positive recognition with areas for improvement

Your narratives should:
- Start with the most important finding (lead with impact)
- Use data to support the story, not overwhelm it
- Include specific examples and context
- End with clear next steps or recommendations
- Be engaging and easy to understand for non-technical leaders

Tone: Professional, insightful, constructive, and action-oriented.
Format: Structured with clear sections but conversational flow."""
    
    def process(self, state: WorkflowState) -> WorkflowState:
        """Generate narrative insights from the analysis results."""
        logger.info("Starting insight narrative generation")
        
        try:
            # Generate executive summary
            executive_summary = self._generate_executive_summary(state)
            
            # Generate detailed narrative
            narrative = self._generate_detailed_narrative(state)
            
            # Generate actionable insights
            actionable_insights = self._generate_actionable_insights(state)
            
            # Generate charts
            charts = self._generate_charts(state)
            
            # Update state
            state["executive_summary"] = executive_summary
            state["narrative"] = narrative
            state["actionable_insights"] = actionable_insights
            state["charts"] = charts
            
            # Store agent-specific data
            state["agent_data"]["insight_narrator"] = {
                "narrative_length": len(narrative),
                "insights_count": len(actionable_insights),
                "charts_generated": len(charts),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            logger.info("Insight narrative generation completed")
            return state
            
        except Exception as e:
            error_msg = f"Insight narrative generation failed: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            raise AgentError("InsightNarrator", error_msg, e)
    
    def _generate_executive_summary(self, state: WorkflowState) -> str:
        """Generate a concise executive summary."""
        
        context = self._prepare_context_for_llm(state)
        
        prompt = """Create a concise executive summary (2-3 sentences) for engineering leadership:

Repository: {repo_name}
Period: {period_summary}
Team: {team_summary}
Key Metrics: {key_metrics}
Top Finding: {top_finding}

Focus on the most important insight that leadership needs to know. What's the headline story?"""
        
        try:
            summary = self._invoke_llm(prompt, context)
            return summary.strip()
        except Exception as e:
            logger.warning(f"Failed to generate executive summary: {e}")
            return f"Engineering productivity analysis for {state['repo_name']} shows {len(state.get('diff_stats', []))} active contributors with {state.get('events_count', 0)} total events."
    
    def _generate_detailed_narrative(self, state: WorkflowState) -> str:
        """Generate a detailed narrative report."""
        
        context = self._prepare_context_for_llm(state)
        
        prompt = """Create a comprehensive productivity narrative for {repo_name}:

## Data Overview
- Period: {period_summary}
- Events: {events_count}
- Contributors: {team_summary}
- Data Quality: {data_quality}

## Key Metrics
{key_metrics}

## Analysis Results
- Diff Stats: {diff_stats_summary}
- DORA Metrics: {dora_summary}
- Anomalies: {anomalies}
- Risk Factors: {risk_factors}

Create a narrative that:
1. Starts with the big picture and key takeaways
2. Highlights team performance and collaboration patterns
3. Discusses both strengths and areas for improvement
4. Contextualizes metrics with business impact
5. Ends with specific recommendations

Keep it engaging, data-driven, and actionable. Aim for 300-500 words."""
        
        try:
            narrative = self._invoke_llm(prompt, context)
            return narrative.strip()
        except Exception as e:
            logger.warning(f"Failed to generate detailed narrative: {e}")
            return self._fallback_narrative(state)
    
    def _generate_actionable_insights(self, state: WorkflowState) -> List[str]:
        """Generate specific actionable insights."""
        
        context = self._prepare_context_for_llm(state)
        
        prompt = """Based on this engineering productivity analysis, provide 3-5 specific, actionable insights:

Context: {context_summary}
Metrics: {key_metrics}
Issues: {issues_summary}

Format each insight as a single, clear sentence that:
- Identifies a specific action or opportunity
- Is implementable by the engineering team
- Has clear business value

Examples:
- "Consider pair programming for developers with high code churn to improve code quality"
- "Implement automated testing to reduce the 23% change failure rate"
- "Recognize John Doe's consistent high-quality contributions with 15 commits and zero reverts"

Return as a simple list, one insight per line."""
        
        try:
            insights_text = self._invoke_llm(prompt, context)
            # Parse insights into list
            insights = [
                line.strip().lstrip('- ').lstrip('• ')
                for line in insights_text.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            return insights[:5]  # Limit to 5 insights
        except Exception as e:
            logger.warning(f"Failed to generate actionable insights: {e}")
            return self._fallback_insights(state)
    
    def _generate_charts(self, state: WorkflowState) -> List[str]:
        """Generate visualization charts for the productivity report."""
        charts = []
        
        try:
            events = state.get("github_events", [])
            diff_stats = state.get("diff_stats", [])
            dora_metrics = state.get("dora_metrics")
            
            # Generate commit activity chart
            if events:
                chart_path = productivity_charts.generate_commit_activity_chart(
                    events, "Commit Activity Timeline"
                )
                charts.append(chart_path)
            
            # Generate contributor comparison chart
            if diff_stats:
                chart_path = productivity_charts.generate_contributor_comparison_chart(
                    diff_stats, "Contributor Productivity"
                )
                charts.append(chart_path)
            
            # Generate DORA metrics chart
            if dora_metrics:
                chart_path = productivity_charts.generate_dora_metrics_chart(
                    dora_metrics, "DORA Four Key Metrics"
                )
                charts.append(chart_path)
            
            # Generate comprehensive dashboard
            if events or diff_stats:
                chart_path = productivity_charts.generate_summary_dashboard(
                    events, diff_stats, dora_metrics, "Productivity Dashboard"
                )
                charts.append(chart_path)
            
            logger.info(f"Generated {len(charts)} charts")
            
            # Clean up old charts
            productivity_charts.cleanup_old_charts()
            
        except Exception as e:
            logger.warning(f"Chart generation failed: {e}")
            # Continue without charts - don't fail the entire process
        
        return charts
    
    def _prepare_context_for_llm(self, state: WorkflowState) -> Dict[str, Any]:
        """Prepare context data for LLM prompts."""
        
        # Basic info
        period_days = (state["period_end"] - state["period_start"]).days
        
        # Team summary
        diff_stats = state.get("diff_stats", [])
        team_info = f"{len(diff_stats)} contributors" if diff_stats else "No contributor data"
        
        # Key metrics summary
        dora_metrics = state.get("dora_metrics")
        key_metrics = []
        
        if diff_stats:
            total_commits = sum(s.commit_count for s in diff_stats)
            total_changes = sum(s.total_additions + s.total_deletions for s in diff_stats)
            key_metrics.append(f"Commits: {total_commits}")
            key_metrics.append(f"Lines changed: {total_changes:,}")
        
        if dora_metrics:
            if dora_metrics.lead_time_hours:
                key_metrics.append(f"Lead time: {dora_metrics.lead_time_hours:.1f}h")
            if dora_metrics.deployment_frequency:
                key_metrics.append(f"Deploy frequency: {dora_metrics.deployment_frequency:.2f}/day")
            if dora_metrics.change_failure_rate:
                key_metrics.append(f"Failure rate: {dora_metrics.change_failure_rate:.1%}")
        
        # Top finding
        top_finding = "Normal development activity"
        if state.get("anomalies"):
            top_finding = state["anomalies"][0]
        elif state.get("risk_factors"):
            top_finding = state["risk_factors"][0]
        
        return {
            "repo_name": state["repo_name"],
            "period_summary": f"{period_days} days ({state['period_start'].strftime('%Y-%m-%d')} to {state['period_end'].strftime('%Y-%m-%d')})",
            "events_count": state.get("events_count", 0),
            "team_summary": team_info,
            "data_quality": f"{state.get('data_quality_score', 0):.1%}",
            "key_metrics": ", ".join(key_metrics) if key_metrics else "No metrics available",
            "top_finding": top_finding,
            "diff_stats_summary": self._summarize_diff_stats(diff_stats),
            "dora_summary": self._summarize_dora_metrics(dora_metrics),
            "anomalies": "; ".join(state.get("anomalies", [])[:3]) or "None detected",
            "risk_factors": "; ".join(state.get("risk_factors", [])[:3]) or "None identified",
            "context_summary": f"{team_info} working on {state['repo_name']} over {period_days} days",
            "issues_summary": self._summarize_issues(state)
        }
    
    def _summarize_diff_stats(self, diff_stats: List[DiffStats]) -> str:
        """Summarize diff statistics."""
        if not diff_stats:
            return "No diff statistics available"
        
        total_commits = sum(s.commit_count for s in diff_stats)
        total_changes = sum(s.total_additions + s.total_deletions for s in diff_stats)
        avg_churn = sum(s.churn_rate for s in diff_stats) / len(diff_stats)
        
        top_contributor = max(diff_stats, key=lambda s: s.commit_count)
        
        return f"{len(diff_stats)} contributors, {total_commits} commits, {total_changes:,} lines changed, avg churn {avg_churn:.2f}, top: {top_contributor.author} ({top_contributor.commit_count} commits)"
    
    def _summarize_dora_metrics(self, dora_metrics: Optional[DORAMetrics]) -> str:
        """Summarize DORA metrics."""
        if not dora_metrics:
            return "DORA metrics not available"
        
        summary_parts = []
        
        if dora_metrics.lead_time_hours:
            summary_parts.append(f"Lead time: {dora_metrics.lead_time_hours:.1f}h")
        
        if dora_metrics.deployment_frequency:
            summary_parts.append(f"Deploy freq: {dora_metrics.deployment_frequency:.2f}/day")
        
        if dora_metrics.change_failure_rate:
            summary_parts.append(f"Failure rate: {dora_metrics.change_failure_rate:.1%}")
        
        if dora_metrics.mttr_hours:
            summary_parts.append(f"MTTR: {dora_metrics.mttr_hours:.1f}h")
        
        return "; ".join(summary_parts) if summary_parts else "Limited DORA data"
    
    def _summarize_issues(self, state: WorkflowState) -> str:
        """Summarize key issues and concerns."""
        issues = []
        
        if state.get("anomalies"):
            issues.extend(state["anomalies"][:2])
        
        if state.get("risk_factors"):
            issues.extend(state["risk_factors"][:2])
        
        if state.get("warnings"):
            issues.extend(state["warnings"][:1])
        
        return "; ".join(issues) if issues else "No significant issues identified"
    
    def _fallback_narrative(self, state: WorkflowState) -> str:
        """Generate a simple fallback narrative when AI generation fails."""
        
        period_days = (state["period_end"] - state["period_start"]).days
        events_count = state.get("events_count", 0)
        diff_stats = state.get("diff_stats", [])
        
        narrative = f"""# Engineering Productivity Report: {state['repo_name']}

## Summary
Analysis of {period_days} days of development activity shows {events_count} events from {len(diff_stats)} contributors.

## Key Findings
"""
        
        if diff_stats:
            total_commits = sum(s.commit_count for s in diff_stats)
            total_changes = sum(s.total_additions + s.total_deletions for s in diff_stats)
            narrative += f"- Team delivered {total_commits} commits with {total_changes:,} lines of code changes\n"
            
            top_contributor = max(diff_stats, key=lambda s: s.commit_count)
            narrative += f"- Most active contributor: {top_contributor.author} ({top_contributor.commit_count} commits)\n"
        
        if state.get("anomalies"):
            narrative += f"- Notable patterns: {'; '.join(state['anomalies'][:2])}\n"
        
        if state.get("dora_metrics"):
            dora = state["dora_metrics"]
            if dora.deployment_frequency:
                narrative += f"- Deployment frequency: {dora.deployment_frequency:.2f} per day\n"
        
        narrative += "\n## Recommendations\n"
        narrative += "Continue monitoring team productivity metrics and consider implementing automated quality checks."
        
        return narrative
    
    def _fallback_insights(self, state: WorkflowState) -> List[str]:
        """Generate fallback insights when AI generation fails."""
        insights = []
        
        diff_stats = state.get("diff_stats", [])
        if diff_stats:
            top_contributor = max(diff_stats, key=lambda s: s.commit_count)
            insights.append(f"Recognize {top_contributor.author}'s productivity with {top_contributor.commit_count} commits")
        
        if state.get("anomalies"):
            insights.append("Investigate code churn anomalies to ensure sustainable development practices")
        
        if state.get("risk_factors"):
            insights.append("Address identified risk factors to improve code quality and team efficiency")
        
        insights.append("Continue regular productivity monitoring to track team performance trends")
        
        return insights[:5]


# Global instance
insight_narrator = InsightNarratorAgent()