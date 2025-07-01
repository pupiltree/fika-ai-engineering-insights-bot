from typing import Dict, Any
from langchain.agents import Tool
from langchain.schema import BaseMessage, HumanMessage

class InsightNarrator:
    """
    LangChain agent responsible for generating narrative summaries and mapping insights to DORA metrics.
    """
    
    def __init__(self):
        self.name = "InsightNarrator"
        self.description = "Generates human-readable narratives from analysis data and maps to DORA metrics"

    def summarize(self, analysis: Dict[str, Any]) -> str:
        """Generate a narrative summary from analysis data"""
        lines = []
        lines.append(f"Total commits: {analysis['commit_count']}")
        lines.append("Commits per author:")
        for author, count in analysis['commits_per_author'].items():
            lines.append(f"  - {author}: {count}")
        lines.append(f"PR throughput: {analysis['pr_throughput']}")
        lines.append(f"Average review latency: {analysis['review_latency_avg']:.2f} hours")
        
        churn = analysis['code_churn']
        lines.append(f"Code churn: +{churn['additions']} / -{churn['deletions']}")
        lines.append(f"Files touched: {analysis['files_touched']}")
        
        # Churn spikes
        if analysis['churn_spikes']:
            lines.append(f"Churn spikes detected in {len(analysis['churn_spikes'])} commits (possible risk)")
        else:
            lines.append("No churn spikes detected.")
        
        # Outlier authors
        if analysis['outlier_authors']:
            lines.append(f"Outlier authors (high churn): {', '.join(analysis['outlier_authors'])}")
        else:
            lines.append("No outlier authors detected.")
        
        # DORA metrics
        dora = analysis['dora_metrics']
        lines.append("\nDORA Metrics:")
        lines.append(f"  - Lead time (avg): {dora['lead_time_hours']:.2f} hours")
        lines.append(f"  - Deploy frequency: {dora['deploy_frequency']}")
        lines.append(f"  - Change failure rate: {dora['change_failure_rate']*100:.1f}%")
        lines.append(f"  - MTTR: {dora['mttr']} (not enough data for real value)")
        
        return '\n'.join(lines)
    
    def get_tool(self) -> Tool:
        """Return a LangChain Tool for this agent"""
        return Tool(
            name="generate_narrative",
            description="Generates human-readable narrative summaries from analysis data",
            func=lambda x: self.summarize(x) if isinstance(x, dict) else "Invalid input"
        )
    
    def process_message(self, message: str, analysis: Dict[str, Any] = None) -> str:
        """Process a message and return narrative summary"""
        if analysis:
            return self.summarize(analysis)
        return "No analysis data provided" 