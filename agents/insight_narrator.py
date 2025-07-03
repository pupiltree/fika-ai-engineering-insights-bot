# agents/insight_narrator.py
import os
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from llm.llm_client import OpenAIClient, LlamaClient
from langchain.schema.messages import SystemMessage, HumanMessage

class InsightNarratorAgent:
    def __init__(self):
        self.name = "InsightNarrator"
        provider = os.getenv("LLM_PROVIDER", "openai")
        if provider == "llama":
            self.llm_client = LlamaClient()
        else:
            self.llm_client = OpenAIClient()
        self.log_dir = os.getenv("NARRATOR_LOG_DIR", "output")
        os.makedirs(self.log_dir, exist_ok=True)

    def _format_dora_metrics(self, dora: Dict, dora_prev: Dict = None, prev_label: str = "last week") -> str:
        if not dora:
            return "No DORA metrics available"
        benchmarks = {
            "lead_time": {"elite": 1, "high": 24, "medium": 168, "low": 720},
            "deploy_frequency": {"elite": 7, "high": 1, "medium": 0.25, "low": 0.02},
            "change_failure_rate": {"elite": 5, "high": 10, "medium": 15, "low": 46},
            "mttr": {"elite": 1, "high": 24, "medium": 168, "low": 720}
        }
        metric_labels = {
            "lead_time": "Lead Time (hrs)",
            "deploy_frequency": "Deploy Frequency (per period)",
            "change_failure_rate": "Change Failure Rate (%)",
            "mttr": "MTTR (hrs)"
        }
        perf_labels = {
            "elite": "Excellent",
            "high": "Good",
            "medium": "Needs Improvement",
            "low": "Poor"
        }
        def get_perf_label(metric, value):
            t = benchmarks[metric]
            if metric == "change_failure_rate":
                if value <= t["elite"]: return perf_labels["elite"]
                elif value <= t["high"]: return perf_labels["high"]
                elif value <= t["medium"]: return perf_labels["medium"]
                else: return perf_labels["low"]
            elif metric == "deploy_frequency":
                if value >= t["elite"]: return perf_labels["elite"]
                elif value >= t["high"]: return perf_labels["high"]
                elif value >= t["medium"]: return perf_labels["medium"]
                else: return perf_labels["low"]
            else:
                if value <= t["elite"]: return perf_labels["elite"]
                elif value <= t["high"]: return perf_labels["high"]
                elif value <= t["medium"]: return perf_labels["medium"]
                else: return perf_labels["low"]
        def get_comment(metric, value, trend):
            if metric == "lead_time":
                if value > 168:
                    return "Lead time is high; review deployment pipeline."
                elif value > 24:
                    return "Lead time could be improved."
                else:
                    return "Lead time is excellent."
            elif metric == "deploy_frequency":
                if value < 1:
                    return "Increase deployment frequency for faster delivery."
                elif value < 7:
                    return "Good deployment pace."
                else:
                    return "Excellent deployment frequency."
            elif metric == "change_failure_rate":
                if value > 15:
                    return "High failure rate; investigate root causes."
                elif value > 5:
                    return "Monitor failure rate for recurring issues."
                else:
                    return "Low failure rate."
            elif metric == "mttr":
                if value > 24:
                    return "MTTR is high; improve incident response."
                elif value > 1:
                    return "MTTR is reasonable."
                else:
                    return "MTTR is excellent."
            return ""
        # Slack-friendly: use bullet list, not table
        lines = []
        for key in ["lead_time", "deploy_frequency", "change_failure_rate", "mttr"]:
            value = dora.get(key, None)
            if value is not None:
                label = metric_labels.get(key, key.replace('_', ' ').title())
                perf = get_perf_label(key, value)
                prev = None
                trend = ""
                if dora_prev and key in dora_prev:
                    prev = dora_prev[key]
                    if prev is not None:
                        if value > prev:
                            trend = "↑"
                        elif value < prev:
                            trend = "↓"
                        else:
                            trend = "→"
                comment = get_comment(key, value, trend)
                if prev is not None:
                    lines.append(f"- *{label}*: {value:.1f} ({perf}) {trend} ({prev_label}: {prev:.1f}) — {comment}")
                else:
                    lines.append(f"- *{label}*: {value:.1f} ({perf}) — {comment}")
        return "\n".join(lines)

    def _format_contributor_stats(self, top_contributors: List[Tuple]) -> str:
        if not top_contributors:
            return "No contributor data available"
        formatted = []
        for i, (author, stats) in enumerate(top_contributors, 1):
            commits = stats.get("commits", 0)
            churn = stats.get("avg_churn", 0)
            formatted.append(f"  {i}. **{author}**: {commits} commits, {churn:.0f} avg churn")
        return "\n".join(formatted)

    def _format_health_indicators(self, risky_count: int, after_hours: int, total_commits: int, avg_churn: float) -> str:
        indicators = []
        risk_percentage = (risky_count / total_commits * 100) if total_commits > 0 else 0
        if risk_percentage > 20:
            indicators.append(f"⚠️  **High Risk**: {risky_count} risky commits ({risk_percentage:.1f}%)")
        elif risk_percentage > 10:
            indicators.append(f"🟡 **Medium Risk**: {risky_count} risky commits ({risk_percentage:.1f}%)")
        else:
            indicators.append(f"🟢 **Low Risk**: {risky_count} risky commits ({risk_percentage:.1f}%)")
        after_hours_percentage = (after_hours / total_commits * 100) if total_commits > 0 else 0
        if after_hours_percentage > 30:
            indicators.append(f"🌙 **High After-Hours Activity**: {after_hours} commits ({after_hours_percentage:.1f}%)")
        elif after_hours_percentage > 15:
            indicators.append(f"🌅 **Moderate After-Hours Activity**: {after_hours} commits ({after_hours_percentage:.1f}%)")
        else:
            indicators.append(f"☀️  **Normal Hours Activity**: {after_hours} commits ({after_hours_percentage:.1f}%)")
        if avg_churn > 1000:
            indicators.append(f"📈 **High Code Churn**: {avg_churn:.0f} lines avg (Consider refactoring)")
        elif avg_churn > 500:
            indicators.append(f"📊 **Moderate Code Churn**: {avg_churn:.0f} lines avg")
        else:
            indicators.append(f"📉 **Low Code Churn**: {avg_churn:.0f} lines avg")
        return "\n".join(indicators)

    def _format_forecast(self, forecast_churn: float, forecast_lead: float, period: str = "weekly") -> str:
        if forecast_churn is None and forecast_lead is None:
            return "Insufficient data for forecasting"
        forecast_items = []
        if period == "daily":
            churn_label = "Tomorrow"
            lead_label = "Tomorrow"
        elif period == "monthly":
            churn_label = "Next Month"
            lead_label = "Next Month"
        else:
            churn_label = "Next Week"
            lead_label = "Next Week"
        if forecast_churn is not None:
            trend = "📈 Increasing" if forecast_churn > 0 else "📉 Decreasing"
            forecast_items.append(f"- **Code Churn**: {abs(forecast_churn):.0f} lines {trend} ({churn_label})")
        if forecast_lead is not None:
            trend = "⏳ Increasing" if forecast_lead > 0 else "⚡ Decreasing"
            forecast_items.append(f"- **Lead Time**: {abs(forecast_lead):.1f} hours {trend} ({lead_label})")
        return "\n".join(forecast_items)

    def run(self, state: Dict, period: str = "weekly") -> Dict:
        """
        period: 'daily', 'weekly', or 'monthly'
        """
        commits = state.get("commits", [])
        analysis = state.get("churn_analysis", {})
        dora = state.get("dora_metrics", {})
        pr_stats = state.get("pr_stats", {})
        after_hours = state.get("after_hours_commits", 0)
        risky_count = state.get("risky_commit_count", 0)
        author_metrics = state.get("author_metrics", {})
        top_contributors = sorted(author_metrics.items(), key=lambda x: x[1].get("commits", 0), reverse=True)[:3]
        dora_prev = state.get("dora_metrics_prev", None)

        # Period-aware date range
        end_date = datetime.now()
        if period == "daily":
            start_date = end_date - timedelta(days=1)
            period_label = "Daily Engineering Report"
            prev_label = "yesterday"
            forecast_label = "Tomorrow Forecast:"
        elif period == "monthly":
            start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
            start_date = start_date.replace(day=1)
            period_label = "Monthly Engineering Report"
            prev_label = "last month"
            forecast_label = "Next Month Forecast:"
        else:
            start_date = end_date - timedelta(days=7)
            period_label = "Weekly Engineering Report"
            prev_label = "last week"
            forecast_label = "Next Week Forecast:"

        # Pass period/prev_label to metric formatting for correct trend text
        dora_formatted = self._format_dora_metrics(dora, dora_prev, prev_label=prev_label)
        contributors_formatted = self._format_contributor_stats(top_contributors)
        health_formatted = self._format_health_indicators(
            risky_count, after_hours, len(commits), analysis.get('avg_churn', 0)
        )
        forecast_formatted = self._format_forecast(
            state.get("forecast_churn"), 
            state.get("forecast_lead_time_hrs"),
            period=period
        )
        # Period-aware prompt
        prompt = f"""
*{period_label}: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}*

*Executive Summary:*
Write a short summary of this {period} engineering activity. Mention whether development pace is improving or declining, highlight any significant risks (e.g., high churn, lead time increase), and summarize overall team health. Do **not** repeat all the metrics.

*Development Activity:*
- Total commits and activity level
- Code churn analysis
- Development velocity trends

*DORA Metrics Performance:*
{dora_formatted}

*Team Health Indicators:*
{health_formatted}

*Top Contributors:*
{contributors_formatted}

*{forecast_label}*
{forecast_formatted}

*Recommendations:*
- 2-3 actionable items based on the data

"""
        # Period-aware system message
        system_msg = f"""You are an experienced Engineering Insights Analyst writing {period} reports for engineering leaders. \
Your reports must:\n\
- Start with a concise, insightful *Executive Summary* that highlights the key trends and concerns.\n\
- Summarize complex data into clear, actionable insights.\n\
- Use engaging yet professional tone: informative, but not overly casual.\n\
- Use clean, well-structured markdown with clear section headings and bullet points.\n\
- Add brief comments on each metric indicating what it means, where we stand vs. benchmarks, and whether it improved or worsened from the previous {period}.\n\
- Make the report easy to skim, focusing on trends, risks, and opportunities.\n\
- Conclude with **practical, high-impact recommendations**, phrased as next steps for the team.\n"""
        result = self.llm_client.generate([
            SystemMessage(content=system_msg),
            HumanMessage(content=prompt)
        ])
        # Log prompt and response for auditability
        # Improved log file naming and metadata
        log_dir = os.path.join(self.log_dir, "logs", period)
        os.makedirs(log_dir, exist_ok=True)
        log_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"narrator_log_{log_time}_{period}.md"
        log_path = os.path.join(log_dir, log_filename)
        # Metadata for log
        metadata = {
            "period": period,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "repo": state.get("repo", "unknown"),
            "log_time": log_time,
            "filename": log_filename
        }
        with open(log_path, "w", encoding="utf-8") as logf:
            logf.write("---\n")
            for k, v in metadata.items():
                logf.write(f"{k}: {v}\n")
            logf.write("---\n\n")
            logf.write("# PROMPT\n\n")
            logf.write(prompt)
            logf.write("\n\n# RESPONSE\n\n")
            logf.write(result.content)
        # Update index.json for this period
        import json
        index_path = os.path.join(log_dir, "index.json")
        try:
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as idxf:
                    index = json.load(idxf)
            else:
                index = []
            index.append(metadata)
            with open(index_path, "w", encoding="utf-8") as idxf:
                json.dump(index, idxf, indent=2)
        except Exception as e:
            print(f"Error updating narrator log index: {e}")
        return {**state, "narrative": result.content}
