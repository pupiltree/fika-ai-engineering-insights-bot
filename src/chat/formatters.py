"""Formatters for Slack reports and messages."""
from datetime import datetime
from typing import Dict, Any, List

from ..graph.state import WorkflowState
from ..data.models import SlackReport, DiffStats, DORAMetrics


def format_slack_report(state: WorkflowState, params: Dict[str, Any]) -> SlackReport:
    """Format workflow results into a Slack-friendly report."""
    
    # Generate title
    period_type = params.get("period_type", "weekly").title()
    repo_name = params.get("repo_name", state["repo_name"])
    title = f"{period_type} Productivity Report: {repo_name}"
    
    # Generate summary
    summary = _generate_summary(state, params)
    
    # Get narrative (truncated for Slack)
    narrative = state.get("narrative", "No detailed analysis available")
    if len(narrative) > 1000:
        narrative = narrative[:1000] + "..."
    
    # Generate metrics table
    metrics_table = _generate_metrics_table(state)
    
    # Get charts (placeholder for now)
    charts = state.get("charts", [])
    
    return SlackReport(
        title=title,
        summary=summary,
        narrative=narrative,
        charts=charts,
        metrics_table=metrics_table
    )


def _generate_summary(state: WorkflowState, params: Dict[str, Any]) -> str:
    """Generate executive summary for Slack."""
    
    # Get basic stats
    events_count = state.get("events_count", 0)
    diff_stats = state.get("diff_stats", [])
    contributors = len(diff_stats)
    
    # Get DORA metrics
    dora = state.get("dora_metrics")
    
    # Get executive summary from AI if available
    exec_summary = state.get("executive_summary")
    if exec_summary:
        return f"*{exec_summary}*\n\n📊 {events_count} events from {contributors} contributors"
    
    # Fallback summary
    if contributors == 0:
        return f"⚠️ No development activity found for the specified period"
    
    # Calculate basic metrics
    if diff_stats:
        total_commits = sum(s.commit_count for s in diff_stats)
        total_changes = sum(s.total_additions + s.total_deletions for s in diff_stats)
        top_contributor = max(diff_stats, key=lambda s: s.commit_count)
        
        summary = f"📈 **{contributors} contributors** delivered **{total_commits} commits** "
        summary += f"with **{total_changes:,} lines changed**\n\n"
        summary += f"🏆 Top contributor: **{top_contributor.author}** ({top_contributor.commit_count} commits)"
        
        # Add DORA insights if available
        if dora:
            if dora.deployment_frequency and dora.deployment_frequency > 0:
                summary += f"\n🚀 Deploy frequency: **{dora.deployment_frequency:.1f}/day**"
            if dora.lead_time_hours:
                summary += f"\n⏱️ Avg lead time: **{dora.lead_time_hours:.1f} hours**"
        
        return summary
    
    return f"📊 Analysis completed with {events_count} events from {contributors} contributors"


def _generate_metrics_table(state: WorkflowState) -> str:
    """Generate a formatted metrics table for Slack."""
    
    diff_stats = state.get("diff_stats", [])
    if not diff_stats:
        return "No metrics available"
    
    # Sort by commit count (descending)
    sorted_stats = sorted(diff_stats, key=lambda s: s.commit_count, reverse=True)
    
    # Create table header
    table = "Author           Commits  +Lines   -Lines   Files\n"
    table += "──────────────────────────────────────────────\n"
    
    # Add rows (limit to top 10)
    for stat in sorted_stats[:10]:
        author = stat.author[:15].ljust(15)  # Truncate and pad
        commits = str(stat.commit_count).rjust(7)
        additions = str(stat.total_additions).rjust(8)
        deletions = str(stat.total_deletions).rjust(8)
        files = str(stat.total_files_changed).rjust(7)
        
        table += f"{author} {commits} {additions} {deletions} {files}\n"
    
    # Add totals
    total_commits = sum(s.commit_count for s in diff_stats)
    total_additions = sum(s.total_additions for s in diff_stats)
    total_deletions = sum(s.total_deletions for s in diff_stats)
    total_files = sum(s.total_files_changed for s in diff_stats)
    
    table += "──────────────────────────────────────────────\n"
    table += f"{'TOTAL':<15} {total_commits:>7} {total_additions:>8} {total_deletions:>8} {total_files:>7}"
    
    return table


def format_anomalies_list(anomalies: List[str], max_items: int = 5) -> str:
    """Format anomalies list for Slack."""
    if not anomalies:
        return "✅ No anomalies detected"
    
    formatted = "🔍 **Detected Anomalies:**\n"
    for i, anomaly in enumerate(anomalies[:max_items]):
        formatted += f"{i+1}. {anomaly}\n"
    
    if len(anomalies) > max_items:
        formatted += f"... and {len(anomalies) - max_items} more"
    
    return formatted


def format_risk_factors(risk_factors: List[str], max_items: int = 3) -> str:
    """Format risk factors for Slack."""
    if not risk_factors:
        return "✅ No significant risks identified"
    
    formatted = "⚠️ **Risk Factors:**\n"
    for i, risk in enumerate(risk_factors[:max_items]):
        formatted += f"• {risk}\n"
    
    return formatted


def format_actionable_insights(insights: List[str], max_items: int = 5) -> str:
    """Format actionable insights for Slack."""
    if not insights:
        return "💡 No specific recommendations available"
    
    formatted = "🎯 **Recommended Actions:**\n"
    for i, insight in enumerate(insights[:max_items]):
        formatted += f"{i+1}. {insight}\n"
    
    return formatted


def format_dora_metrics(dora: DORAMetrics) -> str:
    """Format DORA metrics for Slack."""
    if not dora:
        return "📊 DORA metrics not available"
    
    formatted = "📊 **DORA Four Key Metrics:**\n"
    
    if dora.lead_time_hours is not None:
        formatted += f"⏱️ Lead Time: {dora.lead_time_hours:.1f} hours\n"
    
    if dora.deployment_frequency is not None:
        formatted += f"🚀 Deploy Frequency: {dora.deployment_frequency:.2f} per day\n"
    
    if dora.change_failure_rate is not None:
        formatted += f"❌ Change Failure Rate: {dora.change_failure_rate:.1%}\n"
    
    if dora.mttr_hours is not None:
        formatted += f"🔧 MTTR: {dora.mttr_hours:.1f} hours\n"
    
    return formatted


def format_error_message(error: str, context: str = None) -> str:
    """Format error message for Slack."""
    formatted = f"❌ **Error:** {error}\n"
    
    if context:
        formatted += f"📝 **Context:** {context}\n"
    
    formatted += "\n💡 **Next Steps:**\n"
    formatted += "• Check repository permissions\n"
    formatted += "• Verify API tokens\n"
    formatted += "• Try a different time period"
    
    return formatted


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to fit Slack message limits."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def escape_slack_text(text: str) -> str:
    """Escape special characters for Slack markdown."""
    # Escape characters that have special meaning in Slack
    escape_chars = ['&', '<', '>']
    for char in escape_chars:
        text = text.replace(char, f'&{ord(char):02x};')
    
    return text