"""
Data Harvester agent for collecting GitHub data
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from powerbiz.agents.base_agent import BaseAgent
from powerbiz.github_api.harvester import GitHubDataHarvester
from powerbiz.database.db import get_session
from powerbiz.database.models import Repository, Commit, PullRequest, Review, CIBuild

logger = logging.getLogger(__name__)

class DataHarvesterAgent(BaseAgent):
    """Agent responsible for collecting and processing GitHub data."""
    
    def __init__(self, harvester: Optional[GitHubDataHarvester] = None):
        """Initialize the Data Harvester agent.
        
        Args:
            harvester: GitHub data harvester. If not provided, a new one will be created.
        """
        super().__init__(agent_name="data_harvester")
        self.harvester = harvester or GitHubDataHarvester()
        
        self.system_prompt = """
        You are DataHarvester, an AI agent specialized in analyzing GitHub repository data.
        Your role is to identify patterns in commit and pull request data and extract meaningful
        engineering metrics. You will receive repository statistics and should provide insights about:
        
        1. Commit volume and distribution
        2. Code churn (lines added/removed)
        3. File changes
        4. Pull request throughput and cycle time
        5. Review patterns
        
        Focus on facts and patterns that can be derived from the data. Avoid making assumptions
        about the quality of the code or the effectiveness of the team without direct evidence.
        
        Always summarize key DORA metrics:
        - Deployment Frequency: How often code is deployed to production
        - Lead Time for Changes: Time from code commit to successful deployment
        - Mean Time to Recovery: Time to recover from incidents/failures
        - Change Failure Rate: Percentage of deployments causing failures
        
        Your analysis will be passed to the DiffAnalyst agent, so include all relevant data.
        """
    
    async def harvest_repository_data(
        self,
        owner: str,
        repo: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Harvest data from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days_back: Number of days to look back
            
        Returns:
            Dictionary with harvested repository data summary
        """
        logger.info(f"Harvesting data from {owner}/{repo}")
        
        # Harvest repository
        repository = await self.harvester.harvest_repository(owner, repo)
        
        # Set time range
        until = datetime.utcnow()
        since = until - timedelta(days=days_back)
        
        # Harvest commits
        commits = await self.harvester.harvest_commits(
            owner, repo, repository.id, since=since, until=until
        )
        
        # Harvest pull requests
        pull_requests = await self.harvester.harvest_pull_requests(
            owner, repo, repository.id, state="all", since=since
        )
        
        # Harvest CI builds
        ci_builds = await self.harvester.harvest_ci_builds(
            owner, repo, repository.id, since=since
        )
        
        # Harvest deployments
        deployments = await self.harvester.harvest_deployments(
            owner, repo, repository.id, since=since
        )
        
        # Harvest incidents
        incidents = await self.harvester.harvest_incidents(
            owner, repo, repository.id, since=since
        )
        
        return {
            "repository": repository,
            "commits": commits,
            "pull_requests": pull_requests,
            "ci_builds": ci_builds,
            "deployments": deployments,
            "incidents": incidents,
            "time_range": {
                "since": since,
                "until": until
            }
        }
    
    async def analyze_repository_data(
        self,
        owner: str,
        repo: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze repository data and provide initial insights.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days_back: Number of days to look back
            
        Returns:
            Dictionary with analysis results
        """
        # First, harvest the data
        harvest_results = await self.harvest_repository_data(owner, repo, days_back)
        
        # Prepare repository stats
        repo_stats = self._prepare_repo_stats(
            harvest_results["commits"],
            harvest_results["pull_requests"],
            harvest_results["ci_builds"],
            harvest_results.get("deployments", []),
            harvest_results.get("incidents", [])
        )
        
        # Get LLM insights on the repository data
        insights = await self._get_repo_insights(owner, repo, repo_stats)
        
        # Extract key insights for the DiffAnalyst agent
        key_insights = await self.extract_key_insights(repo_stats, insights)
        
        return {
            "repository": harvest_results["repository"],
            "stats": repo_stats,
            "insights": insights,
            "key_insights": key_insights,
            "time_range": harvest_results["time_range"]
        }
    
    def _prepare_repo_stats(
        self,
        commits: List[Commit],
        pull_requests: List[PullRequest],
        ci_builds: List[Any],
        deployments: List[Any] = None,
        incidents: List[Any] = None
    ) -> Dict[str, Any]:
        """Prepare repository statistics from harvested data.
        
        Args:
            commits: List of commits
            pull_requests: List of pull requests
            ci_builds: List of CI builds
            deployments: List of deployments
            incidents: List of incidents
            
        Returns:
            Dictionary with repository statistics
        """
        # Commit stats
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
        
        # Pull request stats
        open_prs = [pr for pr in pull_requests if pr.state == "open"]
        closed_prs = [pr for pr in pull_requests if pr.state == "closed" and not pr.is_merged]
        merged_prs = [pr for pr in pull_requests if pr.is_merged]
        
        # Calculate PR metrics
        pr_sizes = self._calculate_pr_sizes(pull_requests)
        
        # Calculate lead time stats (PR creation to merge)
        lead_times = [pr.lead_time_minutes for pr in merged_prs if pr.lead_time_minutes is not None]
        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0
        
        # CI build stats
        successful_builds = [b for b in ci_builds if b.status == "success"]
        failed_builds = [b for b in ci_builds if b.status == "failure"]
        
        # Calculate DORA metrics
        dora_metrics = self._calculate_dora_metrics(
            commits=commits,
            pull_requests=merged_prs,
            ci_builds=ci_builds,
            deployments=deployments,
            incidents=incidents
        )
        
        return {
            "commit_stats": {
                "total_commits": len(commits),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_files_changed": total_files_changed,
                "net_lines_changed": total_additions - total_deletions,
                "daily_commit_frequency": len(commits) / max(1, (datetime.utcnow() - min(commit.commit_date for commit in commits if commit.commit_date)).days) if commits else 0,
            },
            "author_stats": author_stats,
            "pr_stats": {
                "total_prs": len(pull_requests),
                "open_prs": len(open_prs),
                "closed_prs": len(closed_prs),
                "merged_prs": len(merged_prs),
                "avg_lead_time_minutes": avg_lead_time,
                "avg_lead_time_hours": avg_lead_time / 60 if avg_lead_time else 0,
                "pr_sizes": pr_sizes,
            },
            "ci_stats": {
                "total_builds": len(ci_builds),
                "successful_builds": len(successful_builds),
                "failed_builds": len(failed_builds),
                "success_rate": len(successful_builds) / len(ci_builds) if ci_builds else 0,
            },
            "dora_metrics": dora_metrics
        }
    
    def _calculate_pr_sizes(self, pull_requests: List[PullRequest]) -> Dict[str, int]:
        """Calculate PR sizes based on number of changes.
        
        Args:
            pull_requests: List of pull requests
            
        Returns:
            Dictionary with PR size distribution
        """
        # Define PR size categories based on changes
        pr_sizes = {
            "xs": 0,  # 0-9 changes
            "small": 0,  # 10-49 changes
            "medium": 0,  # 50-249 changes
            "large": 0,  # 250-999 changes
            "xl": 0,  # 1000+ changes
        }
        
        for pr in pull_requests:
            changes = (pr.additions or 0) + (pr.deletions or 0)
            
            if changes < 10:
                pr_sizes["xs"] += 1
            elif changes < 50:
                pr_sizes["small"] += 1
            elif changes < 250:
                pr_sizes["medium"] += 1
            elif changes < 1000:
                pr_sizes["large"] += 1
            else:
                pr_sizes["xl"] += 1
                
        return pr_sizes
    
    def _calculate_dora_metrics(
        self,
        commits: List[Commit],
        pull_requests: List[PullRequest],
        ci_builds: List[Any],
        deployments: List[Any],
        incidents: List[Any]
    ) -> Dict[str, Any]:
        """Calculate DORA metrics from repository data.
        
        Args:
            commits: List of commits
            pull_requests: List of pull requests (merged only)
            ci_builds: List of CI builds
            deployments: List of deployments
            incidents: List of incidents
            
        Returns:
            Dictionary with DORA metrics
        """
        # Initialize metrics
        metrics = {
            "deployment_frequency": 0,
            "lead_time_for_changes": 0,
            "mean_time_to_recovery": 0,
            "change_failure_rate": 0,
            "deployment_frequency_category": "low",
            "lead_time_category": "low",
            "mttr_category": "low",
            "failure_rate_category": "high"
        }
        
        # Handle empty lists
        if not deployments:
            return metrics
            
        # 1. Deployment Frequency
        days = (deployments[-1].deployment_date - deployments[0].deployment_date).days
        days = max(1, days)  # Avoid division by zero
        metrics["deployment_frequency"] = len(deployments) / days
        
        # Categorize deployment frequency
        if metrics["deployment_frequency"] >= 1:
            metrics["deployment_frequency_category"] = "elite"
        elif metrics["deployment_frequency"] >= 1/7:
            metrics["deployment_frequency_category"] = "high"
        elif metrics["deployment_frequency"] >= 1/30:
            metrics["deployment_frequency_category"] = "medium"
        else:
            metrics["deployment_frequency_category"] = "low"
            
        # 2. Lead Time for Changes (time from commit to deployment)
        if commits and deployments:
            # Map commits to deployments
            lead_times = []
            for commit in commits:
                # Find the first deployment after this commit
                for deploy in deployments:
                    if deploy.deployment_date > commit.commit_date:
                        lead_time = (deploy.deployment_date - commit.commit_date).total_seconds() / 3600  # in hours
                        lead_times.append(lead_time)
                        break
            
            if lead_times:
                metrics["lead_time_for_changes"] = sum(lead_times) / len(lead_times)
                
                # Categorize lead time
                if metrics["lead_time_for_changes"] < 24:
                    metrics["lead_time_category"] = "elite"
                elif metrics["lead_time_for_changes"] < 7 * 24:
                    metrics["lead_time_category"] = "high"
                elif metrics["lead_time_for_changes"] < 30 * 24:
                    metrics["lead_time_category"] = "medium"
                else:
                    metrics["lead_time_category"] = "low"
        
        # 3. Mean Time to Recovery
        if incidents:
            recovery_times = []
            for incident in incidents:
                if incident.resolved_at and incident.created_at:
                    recovery_time = (incident.resolved_at - incident.created_at).total_seconds() / 3600  # in hours
                    recovery_times.append(recovery_time)
            
            if recovery_times:
                metrics["mean_time_to_recovery"] = sum(recovery_times) / len(recovery_times)
                
                # Categorize MTTR
                if metrics["mean_time_to_recovery"] < 1:
                    metrics["mttr_category"] = "elite"
                elif metrics["mean_time_to_recovery"] < 24:
                    metrics["mttr_category"] = "high"
                elif metrics["mean_time_to_recovery"] < 7 * 24:
                    metrics["mttr_category"] = "medium"
                else:
                    metrics["mttr_category"] = "low"
        
        # 4. Change Failure Rate
        if deployments:
            failed_deployments = sum(1 for d in deployments if d.status == "failed")
            metrics["change_failure_rate"] = failed_deployments / len(deployments) if deployments else 0
            
            # Categorize failure rate
            if metrics["change_failure_rate"] < 0.15:
                metrics["failure_rate_category"] = "elite"
            elif metrics["change_failure_rate"] < 0.30:
                metrics["failure_rate_category"] = "high"
            elif metrics["change_failure_rate"] < 0.45:
                metrics["failure_rate_category"] = "medium"
            else:
                metrics["failure_rate_category"] = "low"
        
        return metrics
    
    async def _get_repo_insights(
        self,
        owner: str,
        repo: str,
        repo_stats: Dict[str, Any]
    ) -> str:
        """Get LLM insights on repository data.
        
        Args:
            owner: Repository owner
            repo: Repository name
            repo_stats: Repository statistics
            
        Returns:
            String with insights
        """
        prompt_template = """
        Repository: {owner}/{repo}
        
        Commit Statistics:
        - Total Commits: {commit_stats[total_commits]}
        - Total Lines Added: {commit_stats[total_additions]}
        - Total Lines Deleted: {commit_stats[total_deletions]}
        - Total Files Changed: {commit_stats[total_files_changed]}
        - Daily Commit Frequency: {commit_stats[daily_commit_frequency]:.2f}
        
        Top Contributors:
        {author_summary}
        
        Pull Request Statistics:
        - Total PRs: {pr_stats[total_prs]}
        - Open PRs: {pr_stats[open_prs]}
        - Closed PRs: {pr_stats[closed_prs]}
        - Merged PRs: {pr_stats[merged_prs]}
        - Average Lead Time (hours): {pr_stats[avg_lead_time_hours]:.1f}
        
        PR Size Distribution:
        - XS (0-9 changes): {pr_sizes[xs]}
        - S (10-49 changes): {pr_sizes[small]}
        - M (50-249 changes): {pr_sizes[medium]}
        - L (250-999 changes): {pr_sizes[large]}
        - XL (1000+ changes): {pr_sizes[xl]}
        
        CI Statistics:
        - Total Builds: {ci_stats[total_builds]}
        - Successful Builds: {ci_stats[successful_builds]}
        - Failed Builds: {ci_stats[failed_builds]}
        - Success Rate: {ci_stats[success_rate]:.1%}
        
        DORA Metrics:
        - Deployment Frequency: {dora_metrics[deployment_frequency]:.2f} per day ({dora_metrics[deployment_frequency_category]} performer)
        - Lead Time for Changes: {dora_metrics[lead_time_for_changes]:.1f} hours ({dora_metrics[lead_time_category]} performer)
        - Mean Time to Recovery: {dora_metrics[mean_time_to_recovery]:.1f} hours ({dora_metrics[mttr_category]} performer)
        - Change Failure Rate: {dora_metrics[change_failure_rate]:.1%} ({dora_metrics[failure_rate_category]} performer)
        
        Based on the above statistics, provide a concise summary of the repository activity.
        Focus on factual observations and patterns in the data. Include:
        1. Overall activity level and code velocity
        2. Distribution of work among contributors
        3. Code churn patterns and PR sizes
        4. DORA metrics analysis and what they reveal about the team's performance
        5. Potential areas for improvement based on the metrics
        
        Keep your response to 3-5 short paragraphs and focus on actionable insights.
        """
        
        # Prepare author summary
        authors = list(repo_stats["author_stats"].items())
        authors.sort(key=lambda x: x[1]["commit_count"], reverse=True)
        
        author_summary_lines = []
        for username, stats in authors[:5]:  # Top 5 contributors
            author_summary_lines.append(
                f"- {username}: {stats['commit_count']} commits, "
                f"+{stats['additions']} / -{stats['deletions']} lines, "
                f"{stats['files_changed']} files changed"
            )
        
        author_summary = "\n".join(author_summary_lines)
        
        # Format the prompt
        prompt = prompt_template.format(
            owner=owner,
            repo=repo,
            commit_stats=repo_stats["commit_stats"],
            author_summary=author_summary,
            pr_stats=repo_stats["pr_stats"],
            pr_sizes=repo_stats["pr_stats"]["pr_sizes"],
            ci_stats=repo_stats["ci_stats"],
            dora_metrics=repo_stats["dora_metrics"]
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("repository_insights")
        
        # Get insights from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        return response.generations[0][0].text
    
    async def extract_key_insights(
        self,
        repo_stats: Dict[str, Any],
        insights: str
    ) -> Dict[str, Any]:
        """Extract key insights from repository data for the DiffAnalyst agent.
        
        Args:
            repo_stats: Repository statistics
            insights: LLM-generated insights
            
        Returns:
            Dictionary with key insights
        """
        # Create callback for logging
        callback = self.create_logger_callback("extract_key_insights")
        
        prompt_template = """
        You are analyzing repository data to extract key insights for a diff analyst.
        
        Repository Statistics:
        ```json
        {repo_stats_json}
        ```
        
        Initial Insights:
        ```
        {insights}
        ```
        
        Please extract the following key insights in JSON format:
        1. Velocity Trend: Is development velocity increasing, decreasing, or stable?
        2. Code Health: Based on PR sizes, commit frequency, and build success rate
        3. Team Distribution: Is work evenly distributed or concentrated?
        4. DORA Performance: Summary of the team's DORA metrics performance
        5. Risk Areas: Identify potential areas of concern (large PRs, failing tests, etc.)
        
        Return your response in valid JSON format with the following structure:
        {
            "velocity_trend": string,
            "code_health": string,
            "team_distribution": string,
            "dora_performance": string,
            "risk_areas": [string, string, ...],
            "recommendations": [string, string, ...]
        }
        """
        
        # Format the prompt
        formatted_prompt = prompt_template.format(
            repo_stats_json=json.dumps(repo_stats, default=str, indent=2),
            insights=insights
        )
        
        # Get insights from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=formatted_prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        # Parse the JSON response
        try:
            key_insights = json.loads(response.generations[0][0].text)
        except json.JSONDecodeError:
            # If parsing fails, return a simpler format
            logger.warning("Failed to parse JSON response from LLM")
            key_insights = {
                "velocity_trend": "unknown",
                "code_health": "unknown",
                "team_distribution": "unknown",
                "dora_performance": "unknown",
                "risk_areas": ["Unable to parse insights"],
                "recommendations": ["Review raw data manually"]
            }
        
        return key_insights
    
    async def get_period_data(
        self,
        repository_id: int,
        report_type: str = "weekly",
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get data for a specific time period.
        
        Args:
            repository_id: Database ID of the repository
            report_type: Type of report ("daily", "weekly", "monthly")
            date: Date in format "YYYY-MM-DD" for the report (defaults to today)
            
        Returns:
            Dictionary with data for the period
        """
        session = get_session()
        try:
            # Get repository
            repository = session.query(Repository).filter_by(id=repository_id).first()
            
            if not repository:
                return {"error": f"Repository with ID {repository_id} not found"}
            
            # Parse date
            if date:
                target_date = datetime.fromisoformat(date)
            else:
                target_date = datetime.utcnow()
            
            # Calculate date range
            if report_type == "daily":
                start_date = datetime(target_date.year, target_date.month, target_date.day)
                end_date = start_date + timedelta(days=1)
            elif report_type == "weekly":
                # Start from Monday of the week
                start_date = target_date - timedelta(days=target_date.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
                end_date = start_date + timedelta(days=7)
            elif report_type == "monthly":
                start_date = datetime(target_date.year, target_date.month, 1)
                if target_date.month == 12:
                    end_date = datetime(target_date.year + 1, 1, 1)
                else:
                    end_date = datetime(target_date.year, target_date.month + 1, 1)
            else:
                return {"error": f"Invalid report type: {report_type}"}
            
            # Query data for the period
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= start_date,
                Commit.commit_date < end_date
            ).all()
            
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= start_date,
                PullRequest.created_at < end_date
            ).all()
            
            # Return period data
            return {
                "repository": repository,
                "commits": commits,
                "pull_requests": pull_requests,
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "report_type": report_type
                }
            }
            
        finally:
            session.close()
