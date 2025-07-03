"""
Insight Narrator agent for generating engineering performance narratives
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from powerbiz.agents.base_agent import BaseAgent
from powerbiz.database.db import get_session
from powerbiz.database.models import (
    Repository, Developer, Team, Commit, PullRequest, Deployment, Incident
)

logger = logging.getLogger(__name__)

class InsightNarratorAgent(BaseAgent):
    """Agent responsible for generating engineering performance narratives."""
    
    def __init__(self):
        """Initialize the Insight Narrator agent."""
        super().__init__(agent_name="insight_narrator")
        
        self.system_prompt = """
        You are InsightNarrator, an AI agent specialized in transforming engineering metrics into
        clear, actionable narratives for engineering leaders. Your role is to distill complex data
        into insights that help teams improve their performance and deliver more business value.
        
        Focus on:
        1. DORA metrics (lead time, deployment frequency, change failure rate, MTTR)
        2. Team and individual performance trends
        3. Bottlenecks and opportunities for improvement
        4. Business impact of engineering work
        
        Your narratives should be:
        - Data-driven and specific
        - Balanced (highlighting both strengths and opportunities)
        - Action-oriented (suggesting concrete next steps)
        - Framed in terms of business outcomes, not just technical metrics
        
        Avoid generic advice or platitudes. Ground all insights in the specific data provided
        and explain the reasoning behind your conclusions.
        """
    
    async def generate_daily_report(
        self,
        repository_id: int,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a daily engineering report.
        
        Args:
            repository_id: Database ID of the repository
            date: Date for the report (defaults to current day)
            
        Returns:
            Dictionary with daily report
        """
        logger.info(f"Generating daily report for repository {repository_id}")
        
        # Set time range (just this day)
        if date is None:
            date = datetime.utcnow()
        
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            # Get today's commits
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= start_date,
                Commit.commit_date < end_date
            ).all()
            
            # Get today's PRs
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= start_date,
                PullRequest.created_at < end_date
            ).all()
            
            # Get today's merged PRs
            merged_prs = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.merged_at >= start_date,
                PullRequest.merged_at < end_date
            ).all()
            
            # Get today's deployments
            deployments = session.query(Deployment).filter(
                Deployment.repository_id == repository_id,
                Deployment.deployed_at >= start_date,
                Deployment.deployed_at < end_date
            ).all()
            
            # Get today's incidents
            incidents = session.query(Incident).filter(
                Incident.repository_id == repository_id,
                Incident.detected_at >= start_date,
                Incident.detected_at < end_date
            ).all()
            
            # Prepare daily metrics
            daily_metrics = self._prepare_daily_metrics(
                repository, commits, pull_requests, merged_prs, deployments, incidents
            )
            
            # Generate report narrative
            narrative = await self._generate_daily_narrative(repository, daily_metrics, date)
            
            return {
                "repository": repository,
                "date": date.strftime("%Y-%m-%d"),
                "metrics": daily_metrics,
                "narrative": narrative
            }
        finally:
            session.close()
    
    def _prepare_daily_metrics(
        self,
        repository: Repository,
        commits: List[Commit],
        pull_requests: List[PullRequest],
        merged_prs: List[PullRequest],
        deployments: List[Deployment],
        incidents: List[Incident]
    ) -> Dict[str, Any]:
        """Prepare metrics for daily report.
        
        Args:
            repository: Repository object
            commits: Today's commits
            pull_requests: Today's new PRs
            merged_prs: Today's merged PRs
            deployments: Today's deployments
            incidents: Today's incidents
            
        Returns:
            Dictionary with daily metrics
        """
        # Calculate commit metrics
        total_additions = sum(commit.additions for commit in commits)
        total_deletions = sum(commit.deletions for commit in commits)
        total_files_changed = sum(commit.changed_files for commit in commits)
        
        # Group commits by author
        author_commits = {}
        for commit in commits:
            author_id = commit.developer_id
            if author_id not in author_commits:
                author_commits[author_id] = []
            author_commits[author_id].append(commit)
        
        # Calculate per-author stats
        author_stats = {}
        for author_id, author_commits_list in author_commits.items():
            author = author_commits_list[0].developer
            author_stats[author.github_username] = {
                "name": author.name,
                "commit_count": len(author_commits_list),
                "additions": sum(c.additions for c in author_commits_list),
                "deletions": sum(c.deletions for c in author_commits_list),
                "files_changed": sum(c.changed_files for c in author_commits_list),
            }
        
        # Calculate PR metrics
        pr_additions = sum(pr.additions for pr in pull_requests)
        pr_deletions = sum(pr.deletions for pr in pull_requests)
        
        # Calculate merged PR metrics
        merged_pr_lead_times = [pr.lead_time_minutes for pr in merged_prs if pr.lead_time_minutes is not None]
        avg_lead_time_minutes = sum(merged_pr_lead_times) / len(merged_pr_lead_times) if merged_pr_lead_times else 0
        
        # Calculate incident metrics
        mttr_values = [
            incident.resolution_time_minutes
            for incident in incidents
            if incident.resolution_time_minutes is not None
        ]
        avg_mttr = sum(mttr_values) / len(mttr_values) if mttr_values else 0
        
        return {
            "commit_metrics": {
                "total_commits": len(commits),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_files_changed": total_files_changed,
                "net_lines_changed": total_additions - total_deletions,
                "authors": len(author_commits),
            },
            "author_stats": author_stats,
            "pr_metrics": {
                "new_prs": len(pull_requests),
                "merged_prs": len(merged_prs),
                "pr_additions": pr_additions,
                "pr_deletions": pr_deletions,
                "avg_lead_time_minutes": avg_lead_time_minutes,
                "avg_lead_time_hours": avg_lead_time_minutes / 60 if avg_lead_time_minutes else 0,
            },
            "deployment_metrics": {
                "deployments": len(deployments),
                "production_deployments": len([d for d in deployments if d.environment == "production"]),
            },
            "incident_metrics": {
                "incidents": len(incidents),
                "resolved_incidents": len([i for i in incidents if i.resolved_at is not None]),
                "avg_mttr_minutes": avg_mttr,
                "avg_mttr_hours": avg_mttr / 60 if avg_mttr else 0,
            },
        }
    
    async def _generate_daily_narrative(
        self,
        repository: Repository,
        metrics: Dict[str, Any],
        date: datetime
    ) -> Dict[str, str]:
        """Generate narrative for daily report.
        
        Args:
            repository: Repository object
            metrics: Daily metrics
            date: Report date
            
        Returns:
            Dictionary with report sections
        """
        prompt_template = """
        Daily Engineering Report for {repo_name} on {date_str}
        
        Commit Activity:
        - Total Commits: {commit_metrics[total_commits]}
        - Lines Added: {commit_metrics[total_additions]}
        - Lines Deleted: {commit_metrics[total_deletions]}
        - Net Line Change: {commit_metrics[net_lines_changed]}
        - Files Changed: {commit_metrics[total_files_changed]}
        - Contributing Developers: {commit_metrics[authors]}
        
        {author_summary}
        
        Pull Request Activity:
        - New PRs Opened: {pr_metrics[new_prs]}
        - PRs Merged: {pr_metrics[merged_prs]}
        - Avg Lead Time (hours): {pr_metrics[avg_lead_time_hours]:.1f}
        
        Deployment Activity:
        - Total Deployments: {deployment_metrics[deployments]}
        - Production Deployments: {deployment_metrics[production_deployments]}
        
        Incident Activity:
        - New Incidents: {incident_metrics[incidents]}
        - Resolved Incidents: {incident_metrics[resolved_incidents]}
        - Avg MTTR (hours): {incident_metrics[avg_mttr_hours]:.1f}
        
        Based on this data, please provide a daily engineering report with these sections:
        
        1. Daily Summary: 
           A concise overview of today's engineering activity and any notable events.
        
        2. DORA Metrics Update:
           Brief update on how today's activity affected the team's DORA metrics:
           - Deployment Frequency
           - Lead Time for Changes
           - Change Failure Rate
           - Mean Time to Recovery
        
        3. Highlights and Concerns:
           The most positive developments and any potential areas of concern.
        
        4. Recommendations:
           1-2 specific, actionable recommendations based on today's data.
        
        Keep each section brief and focused on the most important insights. Ensure
        your analysis connects engineering metrics to business outcomes whenever possible.
        """
        
        # Prepare author summary
        authors = list(metrics["author_stats"].items())
        authors.sort(key=lambda x: x[1]["commit_count"], reverse=True)
        
        author_summary_lines = ["Top Contributors:"]
        for username, stats in authors[:3]:  # Top 3 contributors
            author_summary_lines.append(
                f"- {username}: {stats['commit_count']} commits, "
                f"+{stats['additions']} / -{stats['deletions']} lines"
            )
        
        author_summary = "\n".join(author_summary_lines)
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            date_str=date.strftime("%Y-%m-%d"),
            commit_metrics=metrics["commit_metrics"],
            author_summary=author_summary,
            pr_metrics=metrics["pr_metrics"],
            deployment_metrics=metrics["deployment_metrics"],
            incident_metrics=metrics["incident_metrics"]
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("daily_report")
        
        # Get narrative from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        # Parse the response into sections
        narrative_text = response.generations[0][0].text
        
        # Simple section parsing
        sections = {}
        current_section = "preamble"
        sections[current_section] = []
        
        for line in narrative_text.split('\n'):
            if line.strip() == "":
                continue
                
            if any(header in line.lower() for header in ["daily summary", "summary"]):
                current_section = "summary"
                sections[current_section] = []
            elif "dora metrics" in line.lower():
                current_section = "dora_metrics"
                sections[current_section] = []
            elif any(header in line.lower() for header in ["highlights", "concerns"]):
                current_section = "highlights_concerns"
                sections[current_section] = []
            elif "recommendation" in line.lower():
                current_section = "recommendations"
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Convert lists of lines back to text
        for section, lines in sections.items():
            sections[section] = "\n".join(lines)
        
        # Ensure we have all expected sections
        for section in ["summary", "dora_metrics", "highlights_concerns", "recommendations"]:
            if section not in sections:
                sections[section] = ""
        
        return {
            "full_narrative": narrative_text,
            "sections": sections
        }
    
    async def generate_weekly_report(
        self,
        repository_id: int,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a weekly engineering report.
        
        Args:
            repository_id: Database ID of the repository
            end_date: End date for the report (defaults to current day)
            
        Returns:
            Dictionary with weekly report
        """
        logger.info(f"Generating weekly report for repository {repository_id}")
        
        # Set time range (past 7 days)
        if end_date is None:
            end_date = datetime.utcnow()
        
        end_day = datetime(end_date.year, end_date.month, end_date.day)
        start_day = end_day - timedelta(days=7)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            # Get week's commits
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= start_day,
                Commit.commit_date < end_day
            ).all()
            
            # Get week's PRs
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= start_day,
                PullRequest.created_at < end_day
            ).all()
            
            # Get week's merged PRs
            merged_prs = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.merged_at >= start_day,
                PullRequest.merged_at < end_day
            ).all()
            
            # Get week's deployments
            deployments = session.query(Deployment).filter(
                Deployment.repository_id == repository_id,
                Deployment.deployed_at >= start_day,
                Deployment.deployed_at < end_day
            ).all()
            
            # Get week's incidents
            incidents = session.query(Incident).filter(
                Incident.repository_id == repository_id,
                Incident.detected_at >= start_day,
                Incident.detected_at < end_day
            ).all()
            
            # Prepare weekly metrics
            weekly_metrics = self._prepare_weekly_metrics(
                repository, commits, pull_requests, merged_prs, deployments, incidents
            )
            
            # Generate report narrative
            narrative = await self._generate_weekly_narrative(
                repository, weekly_metrics, start_day, end_day
            )
            
            return {
                "repository": repository,
                "start_date": start_day.strftime("%Y-%m-%d"),
                "end_date": end_day.strftime("%Y-%m-%d"),
                "metrics": weekly_metrics,
                "narrative": narrative
            }
        finally:
            session.close()
    
    def _prepare_weekly_metrics(
        self,
        repository: Repository,
        commits: List[Commit],
        pull_requests: List[PullRequest],
        merged_prs: List[PullRequest],
        deployments: List[Deployment],
        incidents: List[Incident]
    ) -> Dict[str, Any]:
        """Prepare metrics for weekly report.
        
        Args:
            repository: Repository object
            commits: Week's commits
            pull_requests: Week's new PRs
            merged_prs: Week's merged PRs
            deployments: Week's deployments
            incidents: Week's incidents
            
        Returns:
            Dictionary with weekly metrics
        """
        # Calculate commit metrics
        total_additions = sum(commit.additions for commit in commits)
        total_deletions = sum(commit.deletions for commit in commits)
        total_files_changed = sum(commit.changed_files for commit in commits)
        
        # Group commits by author
        author_commits = {}
        for commit in commits:
            author_id = commit.developer_id
            if author_id not in author_commits:
                author_commits[author_id] = []
            author_commits[author_id].append(commit)
        
        # Calculate per-author stats
        author_stats = {}
        for author_id, author_commits_list in author_commits.items():
            author = author_commits_list[0].developer
            author_stats[author.github_username] = {
                "name": author.name,
                "commit_count": len(author_commits_list),
                "additions": sum(c.additions for c in author_commits_list),
                "deletions": sum(c.deletions for c in author_commits_list),
                "files_changed": sum(c.changed_files for c in author_commits_list),
            }
        
        # Group PRs by author
        author_prs = {}
        for pr in pull_requests:
            author_id = pr.author_id
            if author_id not in author_prs:
                author_prs[author_id] = []
            author_prs[author_id].append(pr)
        
        # Calculate PR metrics
        pr_additions = sum(pr.additions for pr in pull_requests)
        pr_deletions = sum(pr.deletions for pr in pull_requests)
        
        # Calculate merged PR metrics
        merged_pr_lead_times = [pr.lead_time_minutes for pr in merged_prs if pr.lead_time_minutes is not None]
        avg_lead_time_minutes = sum(merged_pr_lead_times) / len(merged_pr_lead_times) if merged_pr_lead_times else 0
        
        # Calculate daily deployment frequency
        deploy_days = set(d.deployed_at.strftime("%Y-%m-%d") for d in deployments)
        daily_deploy_frequency = len(deploy_days) / 7  # Deployments per day
        
        # Calculate change failure rate
        prod_deployments = [d for d in deployments if d.environment == "production"]
        if prod_deployments:
            change_failure_rate = len(incidents) / len(prod_deployments)
        else:
            change_failure_rate = 0
        
        # Calculate MTTR
        mttr_values = [
            incident.resolution_time_minutes
            for incident in incidents
            if incident.resolution_time_minutes is not None
        ]
        avg_mttr = sum(mttr_values) / len(mttr_values) if mttr_values else 0
        
        # Daily commit volume
        daily_commits = {}
        for commit in commits:
            date_str = commit.commit_date.strftime("%Y-%m-%d")
            if date_str not in daily_commits:
                daily_commits[date_str] = 0
            daily_commits[date_str] += 1
        
        return {
            "commit_metrics": {
                "total_commits": len(commits),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_files_changed": total_files_changed,
                "net_lines_changed": total_additions - total_deletions,
                "authors": len(author_commits),
                "commits_per_day": len(commits) / 7,
                "daily_commits": daily_commits
            },
            "author_stats": author_stats,
            "pr_metrics": {
                "new_prs": len(pull_requests),
                "merged_prs": len(merged_prs),
                "pr_additions": pr_additions,
                "pr_deletions": pr_deletions,
                "avg_lead_time_minutes": avg_lead_time_minutes,
                "avg_lead_time_hours": avg_lead_time_minutes / 60 if avg_lead_time_minutes else 0,
            },
            "dora_metrics": {
                "lead_time_hours": avg_lead_time_minutes / 60 if avg_lead_time_minutes else 0,
                "deployment_frequency_per_day": daily_deploy_frequency,
                "change_failure_rate": change_failure_rate,
                "mttr_hours": avg_mttr / 60 if avg_mttr else 0,
            },
            "deployment_metrics": {
                "deployments": len(deployments),
                "production_deployments": len([d for d in deployments if d.environment == "production"]),
                "deployment_days": len(deploy_days),
            },
            "incident_metrics": {
                "incidents": len(incidents),
                "resolved_incidents": len([i for i in incidents if i.resolved_at is not None]),
                "avg_mttr_minutes": avg_mttr,
                "avg_mttr_hours": avg_mttr / 60 if avg_mttr else 0,
            },
        }
    
    async def _generate_weekly_narrative(
        self,
        repository: Repository,
        metrics: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, str]:
        """Generate narrative for weekly report.
        
        Args:
            repository: Repository object
            metrics: Weekly metrics
            start_date: Start date of the report
            end_date: End date of the report
            
        Returns:
            Dictionary with report sections
        """
        prompt_template = """
        Weekly Engineering Report for {repo_name}
        Period: {start_date} to {end_date}
        
        Commit Activity:
        - Total Commits: {commit_metrics[total_commits]}
        - Lines Added: {commit_metrics[total_additions]}
        - Lines Deleted: {commit_metrics[total_deletions]}
        - Net Line Change: {commit_metrics[net_lines_changed]}
        - Files Changed: {commit_metrics[total_files_changed]}
        - Contributing Developers: {commit_metrics[authors]}
        - Avg. Commits Per Day: {commit_metrics[commits_per_day]:.1f}
        
        {author_summary}
        
        Pull Request Activity:
        - New PRs Opened: {pr_metrics[new_prs]}
        - PRs Merged: {pr_metrics[merged_prs]}
        - Avg Lead Time (hours): {pr_metrics[avg_lead_time_hours]:.1f}
        
        DORA Metrics:
        - Lead Time for Changes (hours): {dora_metrics[lead_time_hours]:.1f}
        - Deployment Frequency: {dora_metrics[deployment_frequency_per_day]:.2f} per day
        - Change Failure Rate: {dora_metrics[change_failure_rate]:.1%}
        - Mean Time to Recovery (hours): {dora_metrics[mttr_hours]:.1f}
        
        Deployment Activity:
        - Total Deployments: {deployment_metrics[deployments]}
        - Production Deployments: {deployment_metrics[production_deployments]}
        - Days with Deployments: {deployment_metrics[deployment_days]} out of 7
        
        Incident Activity:
        - New Incidents: {incident_metrics[incidents]}
        - Resolved Incidents: {incident_metrics[resolved_incidents]}
        - Avg MTTR (hours): {incident_metrics[avg_mttr_hours]:.1f}
        
        Based on this data, please provide a weekly engineering report with these sections:
        
        1. Executive Summary: 
           A concise overview of the week's engineering activity, major accomplishments,
           and any challenges faced.
        
        2. DORA Metrics Analysis:
           How the team is performing on the four key DORA metrics:
           - Deployment Frequency
           - Lead Time for Changes
           - Change Failure Rate
           - Mean Time to Recovery (MTTR)
           
           Compare the team's performance against industry benchmarks:
           - Elite performers: < 1 hour lead time, multiple deployments per day, < 15% failure rate, < 1 hour MTTR
           - High performers: < 1 day lead time, 1+ deployments per day, < 15% failure rate, < 1 day MTTR
           - Medium performers: 1 week - 1 month lead time, 1+ per week, < 30% failure rate, < 1 week MTTR
           - Low performers: > 1 month lead time, < 1 per month, > 30% failure rate, > 1 month MTTR
        
        3. Team Performance:
           Analysis of the team's performance, including workload distribution, 
           and standout individual contributions.
        
        4. Engineering Health:
           Assessment of the codebase health and development practices.
        
        5. Key Recommendations:
           3-4 specific, actionable recommendations to improve performance
           and deliver more business value.
        
        Be direct, specific, and data-driven. Highlight both strengths and areas for improvement.
        Focus on how engineering metrics connect to business outcomes.
        """
        
        # Prepare author summary
        authors = list(metrics["author_stats"].items())
        authors.sort(key=lambda x: x[1]["commit_count"], reverse=True)
        
        author_summary_lines = ["Top Contributors:"]
        for username, stats in authors[:5]:  # Top 5 contributors
            author_summary_lines.append(
                f"- {username}: {stats['commit_count']} commits, "
                f"+{stats['additions']} / -{stats['deletions']} lines"
            )
        
        author_summary = "\n".join(author_summary_lines)
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            commit_metrics=metrics["commit_metrics"],
            author_summary=author_summary,
            pr_metrics=metrics["pr_metrics"],
            dora_metrics=metrics["dora_metrics"],
            deployment_metrics=metrics["deployment_metrics"],
            incident_metrics=metrics["incident_metrics"]
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("weekly_report")
        
        # Get narrative from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        # Parse the response into sections
        narrative_text = response.generations[0][0].text
        
        # Simple section parsing
        sections = {}
        current_section = "preamble"
        sections[current_section] = []
        
        for line in narrative_text.split('\n'):
            if line.strip() == "":
                continue
                
            if any(header in line.lower() for header in ["executive summary", "summary"]):
                current_section = "executive_summary"
                sections[current_section] = []
            elif "dora metrics" in line.lower():
                current_section = "dora_metrics"
                sections[current_section] = []
            elif "team performance" in line.lower():
                current_section = "team_performance"
                sections[current_section] = []
            elif "engineering health" in line.lower():
                current_section = "engineering_health"
                sections[current_section] = []
            elif any(header in line.lower() for header in ["recommendations", "key recommendations"]):
                current_section = "recommendations"
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Convert lists of lines back to text
        for section, lines in sections.items():
            sections[section] = "\n".join(lines)
        
        # Ensure we have all expected sections
        for section in [
            "executive_summary", "dora_metrics", "team_performance",
            "engineering_health", "recommendations"
        ]:
            if section not in sections:
                sections[section] = ""
        
        return {
            "full_narrative": narrative_text,
            "sections": sections
        }
