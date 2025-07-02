from typing import List, Dict, Any
from langchain.agents import Tool
from langchain.schema import BaseMessage, HumanMessage
from utils.metrics import count_commits, commits_per_author, pr_throughput, review_latency_avg, code_churn, files_touched, dora_metrics

class DiffAnalyst:
    """
    LangChain agent responsible for analyzing code churn, flagging spikes, and linking outliers to defect risk.
    """
    
    def __init__(self):
        self.name = "DiffAnalyst"
        self.description = "Analyzes code churn, detects spikes, and identifies risk outliers"

    def analyze(self, github_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze GitHub data and return insights"""
        if github_data is None:
            # Fallback to direct database access
            from fika_db.database import fetch_commits, fetch_pull_requests
            commits = fetch_commits()
            prs = fetch_pull_requests()
        else:
            commits = github_data.get("commits", [])
            prs = github_data.get("pull_requests", [])
        
        analysis = {}
        
        # Basic metrics
        analysis['commit_count'] = count_commits(commits)
        analysis['commits_per_author'] = commits_per_author(commits)
        analysis['pr_throughput'] = pr_throughput(prs)
        analysis['review_latency_avg'] = review_latency_avg(prs)
        analysis['code_churn'] = code_churn(commits)
        analysis['files_touched'] = files_touched(commits)
        analysis['dora_metrics'] = dora_metrics(prs)
        
        # Churn spike detection
        threshold = 100
        spikes = [c for c in commits if (c['additions'] + c['deletions']) > threshold]
        analysis['churn_spikes'] = spikes
        
        # Outlier authors (high churn)
        author_churn = {}
        for c in commits:
            author_churn[c['author']] = author_churn.get(c['author'], 0) + c['additions'] + c['deletions']
        outlier_authors = [a for a, churn in author_churn.items() if churn > threshold]
        analysis['outlier_authors'] = outlier_authors
        
        return analysis
    
    def get_tool(self) -> Tool:
        """Return a LangChain Tool for this agent"""
        return Tool(
            name="analyze_code_churn",
            description="Analyzes code churn, detects spikes, and identifies outlier authors",
            func=lambda x: self.analyze()
        )
    
    def process_message(self, message: str, github_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message and return analysis"""
        return self.analyze(github_data) 