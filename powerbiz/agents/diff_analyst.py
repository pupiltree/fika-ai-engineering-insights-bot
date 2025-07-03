"""
Diff Analyst agent for analyzing code changes and identifying patterns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from powerbiz.agents.base_agent import BaseAgent
from powerbiz.database.db import get_session
from powerbiz.database.models import (
    Repository, Commit, PullRequest, Developer, Review
)

logger = logging.getLogger(__name__)

class DiffAnalystAgent(BaseAgent):
    """Agent responsible for analyzing code diffs and identifying patterns."""
    
    def __init__(self):
        """Initialize the Diff Analyst agent."""
        super().__init__(agent_name="diff_analyst")
        
        self.system_prompt = """
        You are DiffAnalyst, an AI agent specialized in analyzing code changes and identifying patterns
        in developer behavior. Your role is to examine code churn, PR patterns, and other metrics to 
        identify potential risks, bottlenecks, and opportunities for improvement.
        
        Focus on:
        1. Code churn hotspots that might indicate technical debt or design issues
        2. PR size and complexity that could affect review quality
        3. File change patterns that might indicate architectural issues
        4. Outlier detection for unusual commit or PR behavior
        5. Correlation between code churn and defect rates
        
        Base your analysis on concrete metrics and patterns in the data. Be specific about what you observe
        and frame insights in terms of potential risks and opportunities.
        """
    
    async def analyze_code_churn(
        self,
        repository_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze code churn patterns in a repository.
        
        Args:
            repository_id: Database ID of the repository
            days_back: Number of days to look back
            
        Returns:
            Dictionary with code churn analysis results
        """
        logger.info(f"Analyzing code churn for repository {repository_id}")
        
        # Set time range
        until = datetime.utcnow()
        since = until - timedelta(days=days_back)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= since,
                Commit.commit_date <= until
            ).all()
            
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= since,
                PullRequest.created_at <= until
            ).all()
            
            # Prepare churn metrics
            churn_metrics = self._calculate_churn_metrics(commits, pull_requests)
            
            # Get LLM analysis
            analysis = await self._analyze_churn_patterns(repository, churn_metrics)
            
            return {
                "repository": repository,
                "metrics": churn_metrics,
                "analysis": analysis,
                "time_range": {
                    "since": since,
                    "until": until
                }
            }
        finally:
            session.close()
    
    def _calculate_churn_metrics(
        self,
        commits: List[Commit],
        pull_requests: List[PullRequest]
    ) -> Dict[str, Any]:
        """Calculate code churn metrics from commits and PRs.
        
        Args:
            commits: List of commits
            pull_requests: List of pull requests
            
        Returns:
            Dictionary with code churn metrics
        """
        # Group commits by author
        author_commits = {}
        for commit in commits:
            author_id = commit.developer_id
            if author_id not in author_commits:
                author_commits[author_id] = []
            author_commits[author_id].append(commit)
        
        # Calculate per-author churn metrics
        author_churn = {}
        for author_id, author_commits_list in author_commits.items():
            author = author_commits_list[0].developer
            author_churn[author.github_username] = {
                "name": author.name,
                "commit_count": len(author_commits_list),
                "additions": sum(c.additions for c in author_commits_list),
                "deletions": sum(c.deletions for c in author_commits_list),
                "files_changed": sum(c.changed_files for c in author_commits_list),
                "net_lines": sum(c.additions for c in author_commits_list) - sum(c.deletions for c in author_commits_list),
                "churn_ratio": sum(c.additions + c.deletions for c in author_commits_list) / len(author_commits_list) if author_commits_list else 0,
            }
        
        # Calculate PR size distribution
        pr_sizes = []
        for pr in pull_requests:
            size = pr.additions + pr.deletions
            if size < 50:
                category = "small"
            elif size < 300:
                category = "medium"
            elif size < 1000:
                category = "large"
            else:
                category = "extra_large"
            
            pr_sizes.append({
                "id": pr.id,
                "title": pr.title,
                "size": size,
                "category": category,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "files_changed": pr.changed_files,
                "author": pr.author.github_username,
                "review_count": pr.review_count,
                "lead_time_hours": pr.lead_time_minutes / 60 if pr.lead_time_minutes else None,
            })
        
        # Calculate team-level metrics
        team_metrics = {
            "total_commits": len(commits),
            "total_additions": sum(c.additions for c in commits),
            "total_deletions": sum(c.deletions for c in commits),
            "total_files_changed": sum(c.changed_files for c in commits),
            "total_churn": sum(c.additions + c.deletions for c in commits),
            "net_lines": sum(c.additions for c in commits) - sum(c.deletions for c in commits),
            "avg_churn_per_commit": sum(c.additions + c.deletions for c in commits) / len(commits) if commits else 0,
        }
        
        # PR size distribution
        pr_size_distribution = {
            "small": len([pr for pr in pr_sizes if pr["category"] == "small"]),
            "medium": len([pr for pr in pr_sizes if pr["category"] == "medium"]),
            "large": len([pr for pr in pr_sizes if pr["category"] == "large"]),
            "extra_large": len([pr for pr in pr_sizes if pr["category"] == "extra_large"]),
        }
        
        return {
            "author_churn": author_churn,
            "team_metrics": team_metrics,
            "pr_sizes": pr_sizes,
            "pr_size_distribution": pr_size_distribution,
        }
    
    async def _analyze_churn_patterns(
        self,
        repository: Repository,
        churn_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get LLM analysis of churn patterns.
        
        Args:
            repository: Repository object
            churn_metrics: Code churn metrics
            
        Returns:
            Dictionary with churn analysis
        """
        prompt_template = """
        Repository: {repo_name}
        
        Team Metrics:
        - Total Commits: {team_metrics[total_commits]}
        - Total Churn (lines changed): {team_metrics[total_churn]}
        - Total Additions: {team_metrics[total_additions]}
        - Total Deletions: {team_metrics[total_deletions]}
        - Net Line Change: {team_metrics[net_lines]}
        - Average Churn per Commit: {team_metrics[avg_churn_per_commit]:.1f}
        
        Top Contributors by Churn:
        {author_summary}
        
        Pull Request Size Distribution:
        - Small (<50 lines): {pr_size_distribution[small]}
        - Medium (50-300 lines): {pr_size_distribution[medium]}
        - Large (300-1000 lines): {pr_size_distribution[large]}
        - Extra Large (>1000 lines): {pr_size_distribution[extra_large]}
        
        {large_prs_section}
        
        Based on these metrics, provide an analysis that covers:
        
        1. Code Churn Patterns:
           - Are there outliers in terms of churn?
           - Is the churn distributed evenly or concentrated in a few developers?
           - Are there any potential risks from high churn areas?
        
        2. PR Size Analysis:
           - How healthy is the PR size distribution?
           - What risks might be associated with the observed PR sizes?
           - How might the PR sizes affect review quality and defect rates?
        
        3. Development Velocity:
           - What can we infer about the development pace?
           - Are there any bottlenecks or inefficiencies suggested by the data?
        
        4. Risk Assessment:
           - Based on research showing correlation between code churn and defect rates, 
             which areas might need more careful testing or review?
           - Are there any contributors whose patterns indicate they might need more support?
        
        Your analysis should be data-driven, specific to the patterns observed, and focused on
        actionable insights. Focus on concrete observations rather than general best practices.
        """
        
        # Prepare author summary
        authors = list(churn_metrics["author_churn"].items())
        authors.sort(key=lambda x: x[1]["additions"] + x[1]["deletions"], reverse=True)
        
        author_summary_lines = []
        for username, stats in authors[:5]:  # Top 5 contributors
            author_summary_lines.append(
                f"- {username}: {stats['commit_count']} commits, "
                f"+{stats['additions']} / -{stats['deletions']} lines, "
                f"Churn ratio: {stats['churn_ratio']:.1f} lines/commit"
            )
        
        author_summary = "\n".join(author_summary_lines)
        
        # Prepare large PRs section
        large_prs = [
            pr for pr in churn_metrics["pr_sizes"]
            if pr["category"] in ["large", "extra_large"]
        ]
        large_prs.sort(key=lambda x: x["size"], reverse=True)
        
        if large_prs:
            large_prs_lines = ["Large and Extra Large PRs:"]
            for pr in large_prs[:3]:  # Top 3 largest PRs
                large_prs_lines.append(
                    f"- {pr['title'][:50]}...: {pr['size']} lines changed, "
                    f"{pr['files_changed']} files, {pr['review_count']} reviews, "
                    f"Lead time: {pr['lead_time_hours']:.1f} hours" if pr["lead_time_hours"] else "Not merged"
                )
            large_prs_section = "\n".join(large_prs_lines)
        else:
            large_prs_section = "No large PRs in this time period."
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            team_metrics=churn_metrics["team_metrics"],
            author_summary=author_summary,
            pr_size_distribution=churn_metrics["pr_size_distribution"],
            large_prs_section=large_prs_section
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("churn_analysis")
        
        # Get analysis from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        # Parse the response into sections
        analysis_text = response.generations[0][0].text
        
        # Simple section parsing
        sections = {}
        current_section = "overview"
        sections[current_section] = []
        
        for line in analysis_text.split('\n'):
            if line.strip() == "":
                continue
                
            if line.startswith('#'):
                # It's a heading
                current_section = line.strip('#').strip().lower().replace(' ', '_')
                sections[current_section] = []
            elif any(marker in line.lower() for marker in ["churn pattern", "code churn"]):
                current_section = "churn_patterns"
                sections[current_section] = [line]
            elif any(marker in line.lower() for marker in ["pr size", "pull request size"]):
                current_section = "pr_size_analysis"
                sections[current_section] = [line]
            elif any(marker in line.lower() for marker in ["development velocity", "development pace"]):
                current_section = "development_velocity"
                sections[current_section] = [line]
            elif any(marker in line.lower() for marker in ["risk", "defect"]):
                current_section = "risk_assessment"
                sections[current_section] = [line]
            else:
                sections[current_section].append(line)
        
        # Convert lists of lines back to text
        for section, lines in sections.items():
            sections[section] = "\n".join(lines)
        
        # Ensure we have all expected sections
        for section in ["churn_patterns", "pr_size_analysis", "development_velocity", "risk_assessment"]:
            if section not in sections:
                sections[section] = ""
        
        return {
            "raw_analysis": analysis_text,
            "sections": sections
        }
    
    async def analyze_defect_risk(
        self,
        repository_id: int,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Analyze defect risk based on code churn patterns.
        
        Args:
            repository_id: Database ID of the repository
            days_back: Number of days to look back
            
        Returns:
            Dictionary with defect risk analysis
        """
        logger.info(f"Analyzing defect risk for repository {repository_id}")
        
        # Set time range
        until = datetime.utcnow()
        since = until - timedelta(days=days_back)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= since,
                Commit.commit_date <= until
            ).all()
            
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= since,
                PullRequest.created_at <= until
            ).all()
            
            # Calculate defect risk metrics
            risk_metrics = self._calculate_defect_risk_metrics(commits, pull_requests)
            
            # Get LLM analysis
            analysis = await self._analyze_defect_risks(repository, risk_metrics)
            
            return {
                "repository": repository,
                "metrics": risk_metrics,
                "analysis": analysis,
                "time_range": {
                    "since": since,
                    "until": until
                }
            }
        finally:
            session.close()
    
    def _calculate_defect_risk_metrics(
        self,
        commits: List[Commit],
        pull_requests: List[PullRequest]
    ) -> Dict[str, Any]:
        """Calculate metrics related to defect risk.
        
        Args:
            commits: List of commits
            pull_requests: List of pull requests
            
        Returns:
            Dictionary with defect risk metrics
        """
        # Identify high-churn commits (potential risk)
        high_churn_threshold = 300  # More than 300 lines changed
        high_churn_commits = [
            {
                "id": c.id,
                "sha": c.sha,
                "message": c.message,
                "additions": c.additions,
                "deletions": c.deletions,
                "total_churn": c.additions + c.deletions,
                "author": c.developer.github_username,
                "date": c.commit_date
            }
            for c in commits
            if c.additions + c.deletions > high_churn_threshold
        ]
        
        # Identify large PRs (potential risk)
        large_pr_threshold = 500  # More than 500 lines changed
        large_prs = [
            {
                "id": pr.id,
                "title": pr.title,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "total_churn": pr.additions + pr.deletions,
                "files_changed": pr.changed_files,
                "author": pr.author.github_username,
                "review_count": pr.review_count,
                "created_at": pr.created_at,
                "merged_at": pr.merged_at
            }
            for pr in pull_requests
            if pr.additions + pr.deletions > large_pr_threshold
        ]
        
        # Identify PRs with few or no reviews (potential risk)
        low_review_threshold = 1  # Less than or equal to 1 review
        low_review_prs = [
            {
                "id": pr.id,
                "title": pr.title,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "total_churn": pr.additions + pr.deletions,
                "files_changed": pr.changed_files,
                "author": pr.author.github_username,
                "review_count": pr.review_count,
                "created_at": pr.created_at,
                "merged_at": pr.merged_at
            }
            for pr in pull_requests
            if pr.is_merged and pr.review_count <= low_review_threshold
        ]
        
        # Calculate daily churn over time
        daily_churn = {}
        for commit in commits:
            date_str = commit.commit_date.strftime("%Y-%m-%d")
            if date_str not in daily_churn:
                daily_churn[date_str] = {
                    "date": date_str,
                    "additions": 0,
                    "deletions": 0,
                    "commit_count": 0
                }
            
            daily_churn[date_str]["additions"] += commit.additions
            daily_churn[date_str]["deletions"] += commit.deletions
            daily_churn[date_str]["commit_count"] += 1
        
        # Convert daily_churn to list and sort by date
        daily_churn_list = list(daily_churn.values())
        daily_churn_list.sort(key=lambda x: x["date"])
        
        # Calculate overall risk metrics
        high_churn_commit_ratio = len(high_churn_commits) / len(commits) if commits else 0
        large_pr_ratio = len(large_prs) / len(pull_requests) if pull_requests else 0
        low_review_ratio = len(low_review_prs) / len([pr for pr in pull_requests if pr.is_merged]) if any(pr.is_merged for pr in pull_requests) else 0
        
        return {
            "high_churn_commits": high_churn_commits,
            "large_prs": large_prs,
            "low_review_prs": low_review_prs,
            "daily_churn": daily_churn_list,
            "risk_metrics": {
                "high_churn_commit_ratio": high_churn_commit_ratio,
                "large_pr_ratio": large_pr_ratio,
                "low_review_ratio": low_review_ratio,
                "total_high_risk_commits": len(high_churn_commits),
                "total_high_risk_prs": len(large_prs) + len(low_review_prs)
            }
        }
    
    async def _analyze_defect_risks(
        self,
        repository: Repository,
        risk_metrics: Dict[str, Any]
    ) -> str:
        """Get LLM analysis of defect risks.
        
        Args:
            repository: Repository object
            risk_metrics: Defect risk metrics
            
        Returns:
            String with defect risk analysis
        """
        prompt_template = """
        Repository: {repo_name}
        
        Risk Metrics:
        - High-churn commit ratio: {risk_metrics[high_churn_commit_ratio]:.2%}
        - Large PR ratio: {risk_metrics[large_pr_ratio]:.2%}
        - Low-review PR ratio: {risk_metrics[low_review_ratio]:.2%}
        - Total high-risk commits: {risk_metrics[total_high_risk_commits]}
        - Total high-risk PRs: {risk_metrics[total_high_risk_prs]}
        
        {high_churn_commits_section}
        
        {low_review_prs_section}
        
        Based on research showing strong correlation between code churn and defect rates,
        analyze the defect risk for this repository. Focus on:
        
        1. Overall Risk Assessment:
           - What is the general level of defect risk based on these metrics?
           - Are there specific areas or patterns that indicate higher risk?
        
        2. Risk Factors:
           - Which risk factors (high churn, large PRs, low review coverage) appear most concerning?
           - Are the risks concentrated in specific areas or distributed across the codebase?
        
        3. Mitigation Recommendations:
           - What specific actions could reduce defect risk in this repository?
           - How might the team adjust their development practices based on these findings?
        
        4. Monitoring Strategy:
           - Which metrics should be closely monitored going forward?
           - What thresholds or patterns would indicate improving or worsening risk?
        
        Provide concrete, data-driven insights rather than generic best practices. Refer to specific
        patterns in the data and explain why they indicate potential risk. Your analysis should help 
        the team make informed decisions about where to focus their quality efforts.
        """
        
        # Prepare high churn commits section
        high_churn_commits = risk_metrics["high_churn_commits"]
        high_churn_commits.sort(key=lambda x: x["total_churn"], reverse=True)
        
        if high_churn_commits:
            high_churn_lines = ["Top High-Churn Commits (Potential Risk):"]
            for commit in high_churn_commits[:3]:  # Top 3 highest churn
                high_churn_lines.append(
                    f"- {commit['sha'][:7]}: {commit['message'][:50]}... "
                    f"by {commit['author']}, {commit['total_churn']} lines changed"
                )
            high_churn_commits_section = "\n".join(high_churn_lines)
        else:
            high_churn_commits_section = "No high-churn commits in this time period."
        
        # Prepare low review PRs section
        low_review_prs = risk_metrics["low_review_prs"]
        if low_review_prs:
            low_review_lines = ["Merged PRs with Low Review Coverage (Potential Risk):"]
            for pr in low_review_prs[:3]:  # Top 3 examples
                low_review_lines.append(
                    f"- {pr['title'][:50]}... by {pr['author']}, "
                    f"{pr['total_churn']} lines changed, {pr['review_count']} reviews"
                )
            low_review_prs_section = "\n".join(low_review_lines)
        else:
            low_review_prs_section = "No PRs with low review coverage in this time period."
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            risk_metrics=risk_metrics["risk_metrics"],
            high_churn_commits_section=high_churn_commits_section,
            low_review_prs_section=low_review_prs_section
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("defect_risk_analysis")
        
        # Get analysis from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        return response.generations[0][0].text
    
    async def forecast_metrics(
        self,
        repository_id: int,
        forecast_days: int = 7,
        historical_days: int = 60
    ) -> Dict[str, Any]:
        """Forecast next week's cycle time and churn based on historical data.
        
        Args:
            repository_id: Database ID of the repository
            forecast_days: Number of days to forecast (default: 7 for next week)
            historical_days: Number of historical days to analyze for trends
            
        Returns:
            Dictionary with forecast analysis
        """
        logger.info(f"Forecasting metrics for repository {repository_id}")
        
        # Set time range
        until = datetime.utcnow()
        since = until - timedelta(days=historical_days)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            commits = session.query(Commit).filter(
                Commit.repository_id == repository_id,
                Commit.commit_date >= since,
                Commit.commit_date <= until
            ).all()
            
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= since,
                PullRequest.created_at <= until,
                PullRequest.is_merged == True
            ).all()
            
            # Calculate historical trends
            trends = self._calculate_historical_trends(commits, pull_requests, historical_days)
            
            # Generate forecasts
            forecasts = self._generate_forecasts(trends, forecast_days)
            
            # Get LLM insights on forecasts
            analysis = await self._analyze_forecasts(repository, trends, forecasts)
            
            return {
                "repository": repository,
                "historical_trends": trends,
                "forecasts": forecasts,
                "analysis": analysis,
                "forecast_period": {
                    "start_date": until,
                    "end_date": until + timedelta(days=forecast_days),
                    "forecast_days": forecast_days
                }
            }
        finally:
            session.close()
    
    def _calculate_historical_trends(
        self,
        commits: List[Commit],
        pull_requests: List[PullRequest],
        days: int
    ) -> Dict[str, Any]:
        """Calculate historical trends for forecasting.
        
        Args:
            commits: List of commits
            pull_requests: List of pull requests
            days: Number of days in the period
            
        Returns:
            Dictionary with historical trend data
        """
        # Group data by week for trend analysis
        weekly_data = {}
        
        for commit in commits:
            # Get week start (Monday)
            week_start = commit.commit_date - timedelta(days=commit.commit_date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "week_start": week_start,
                    "commits": 0,
                    "additions": 0,
                    "deletions": 0,
                    "churn": 0,
                    "files_changed": 0,
                    "prs_merged": 0,
                    "cycle_times": []
                }
            
            weekly_data[week_key]["commits"] += 1
            weekly_data[week_key]["additions"] += commit.additions
            weekly_data[week_key]["deletions"] += commit.deletions
            weekly_data[week_key]["churn"] += commit.additions + commit.deletions
            weekly_data[week_key]["files_changed"] += commit.changed_files
        
        # Add PR cycle times by week
        for pr in pull_requests:
            if pr.merged_at and pr.lead_time_minutes:
                week_start = pr.merged_at - timedelta(days=pr.merged_at.weekday())
                week_key = week_start.strftime("%Y-%m-%d")
                
                if week_key in weekly_data:
                    weekly_data[week_key]["prs_merged"] += 1
                    weekly_data[week_key]["cycle_times"].append(pr.lead_time_minutes / 60)  # Convert to hours
        
        # Calculate averages and trends
        weeks = sorted(weekly_data.values(), key=lambda x: x["week_start"])
        
        # Calculate moving averages and trends
        churn_values = [week["churn"] for week in weeks]
        cycle_time_values = [
            sum(week["cycle_times"]) / len(week["cycle_times"]) if week["cycle_times"] else 0
            for week in weeks
        ]
        
        # Simple linear trend calculation
        def calculate_trend(values):
            if len(values) < 2:
                return 0
            x_values = list(range(len(values)))
            n = len(values)
            sum_x = sum(x_values)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(x_values, values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope (trend)
            if n * sum_x2 - sum_x * sum_x == 0:
                return 0
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
        
        churn_trend = calculate_trend(churn_values)
        cycle_time_trend = calculate_trend(cycle_time_values)
        
        return {
            "weekly_data": weeks,
            "churn_trend": churn_trend,
            "cycle_time_trend": cycle_time_trend,
            "avg_weekly_churn": sum(churn_values) / len(churn_values) if churn_values else 0,
            "avg_cycle_time": sum(cycle_time_values) / len(cycle_time_values) if cycle_time_values else 0,
            "churn_values": churn_values,
            "cycle_time_values": cycle_time_values
        }
    
    def _generate_forecasts(self, trends: Dict[str, Any], forecast_days: int) -> Dict[str, Any]:
        """Generate forecasts based on historical trends.
        
        Args:
            trends: Historical trend data
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with forecast values
        """
        # Calculate forecast multiplier (assume linear trend continues)
        weeks_to_forecast = forecast_days / 7
        
        # Forecast churn
        predicted_churn = trends["avg_weekly_churn"] + (trends["churn_trend"] * weeks_to_forecast)
        predicted_churn = max(0, predicted_churn)  # Ensure non-negative
        
        # Forecast cycle time
        predicted_cycle_time = trends["avg_cycle_time"] + (trends["cycle_time_trend"] * weeks_to_forecast)
        predicted_cycle_time = max(0, predicted_cycle_time)  # Ensure non-negative
        
        # Calculate confidence based on trend consistency
        churn_volatility = self._calculate_volatility(trends["churn_values"])
        cycle_time_volatility = self._calculate_volatility(trends["cycle_time_values"])
        
        # Confidence is higher when volatility is lower
        churn_confidence = max(0.1, 1.0 - (churn_volatility / trends["avg_weekly_churn"]) if trends["avg_weekly_churn"] > 0 else 0.5)
        cycle_time_confidence = max(0.1, 1.0 - (cycle_time_volatility / trends["avg_cycle_time"]) if trends["avg_cycle_time"] > 0 else 0.5)
        
        return {
            "predicted_weekly_churn": predicted_churn,
            "predicted_cycle_time_hours": predicted_cycle_time,
            "churn_confidence": min(1.0, churn_confidence),
            "cycle_time_confidence": min(1.0, cycle_time_confidence),
            "trend_direction": {
                "churn": "increasing" if trends["churn_trend"] > 0 else "decreasing" if trends["churn_trend"] < 0 else "stable",
                "cycle_time": "increasing" if trends["cycle_time_trend"] > 0 else "decreasing" if trends["cycle_time_trend"] < 0 else "stable"
            }
        }
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Standard deviation
        """
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    async def _analyze_forecasts(
        self,
        repository: Repository,
        trends: Dict[str, Any],
        forecasts: Dict[str, Any]
    ) -> str:
        """Get LLM analysis of forecast data.
        
        Args:
            repository: Repository object
            trends: Historical trend data
            forecasts: Forecast predictions
            
        Returns:
            String with forecast analysis
        """
        prompt_template = """
        Repository: {repo_name}
        
        Historical Trends (last {weeks} weeks):
        - Average Weekly Churn: {avg_weekly_churn:.0f} lines
        - Average Cycle Time: {avg_cycle_time:.1f} hours
        - Churn Trend: {churn_trend:.1f} lines/week change
        - Cycle Time Trend: {cycle_time_trend:.1f} hours/week change
        
        Next Week Forecast:
        - Predicted Churn: {predicted_churn:.0f} lines (confidence: {churn_confidence:.0%})
        - Predicted Cycle Time: {predicted_cycle_time:.1f} hours (confidence: {cycle_time_confidence:.0%})
        - Churn Direction: {churn_direction}
        - Cycle Time Direction: {cycle_time_direction}
        
        Based on these forecasts and trends, provide analysis covering:
        
        1. Forecast Reliability:
           - How reliable are these predictions based on historical patterns?
           - What factors might affect the accuracy of these forecasts?
        
        2. Trend Analysis:
           - What do the trends indicate about team velocity and practices?
           - Are the trends sustainable or might they indicate problems?
        
        3. Operational Planning:
           - How should the team prepare for next week based on these forecasts?
           - What capacity planning considerations arise from these predictions?
        
        4. Risk Indicators:
           - Do the forecasts suggest any risks that should be monitored?
           - What early warning signs should the team watch for?
        
        Provide actionable insights that help with sprint planning and resource allocation.
        """
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            weeks=len(trends["weekly_data"]),
            avg_weekly_churn=trends["avg_weekly_churn"],
            avg_cycle_time=trends["avg_cycle_time"],
            churn_trend=trends["churn_trend"],
            cycle_time_trend=trends["cycle_time_trend"],
            predicted_churn=forecasts["predicted_weekly_churn"],
            predicted_cycle_time=forecasts["predicted_cycle_time_hours"],
            churn_confidence=forecasts["churn_confidence"],
            cycle_time_confidence=forecasts["cycle_time_confidence"],
            churn_direction=forecasts["trend_direction"]["churn"],
            cycle_time_direction=forecasts["trend_direction"]["cycle_time"]
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("forecast_analysis")
        
        # Get analysis from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        return response.generations[0][0].text
    
    async def generate_influence_map(
        self,
        repository_id: int,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Generate a code review influence map showing collaboration patterns.
        
        This is a stretch goal feature that creates a graph of who reviews whose code,
        helping identify knowledge bottlenecks and collaboration patterns.
        
        Args:
            repository_id: Database ID of the repository
            days_back: Number of days to look back
            
        Returns:
            Dictionary with influence map data and analysis
        """
        logger.info(f"Generating influence map for repository {repository_id}")
        
        # Set time range
        until = datetime.utcnow()
        since = until - timedelta(days=days_back)
        
        # Get data from database
        session = get_session()
        try:
            repository = session.query(Repository).get(repository_id)
            
            # Get pull requests with reviews
            pull_requests = session.query(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                PullRequest.created_at >= since,
                PullRequest.created_at <= until,
                PullRequest.review_count > 0
            ).all()
            
            # Get reviews
            reviews = session.query(Review).join(PullRequest).filter(
                PullRequest.repository_id == repository_id,
                Review.created_at >= since,
                Review.created_at <= until
            ).all()
            
            # Build influence map
            influence_data = self._build_influence_map(pull_requests, reviews)
            
            # Get LLM analysis of the influence patterns
            analysis = await self._analyze_influence_patterns(repository, influence_data)
            
            return {
                "repository": repository,
                "influence_map": influence_data,
                "analysis": analysis,
                "time_range": {
                    "since": since,
                    "until": until
                }
            }
        finally:
            session.close()
    
    def _build_influence_map(
        self,
        pull_requests: List[PullRequest],
        reviews: List[Review]
    ) -> Dict[str, Any]:
        """Build the influence map data structure.
        
        Args:
            pull_requests: List of pull requests
            reviews: List of reviews
            
        Returns:
            Dictionary with influence map data
        """
        # Track author -> reviewer relationships
        review_relationships = {}
        reviewer_stats = {}
        author_stats = {}
        
        for pr in pull_requests:
            author = pr.author.github_username
            
            if author not in author_stats:
                author_stats[author] = {
                    "name": pr.author.name,
                    "prs_created": 0,
                    "total_reviews_received": 0,
                    "unique_reviewers": set(),
                    "avg_pr_size": 0,
                    "total_pr_size": 0
                }
            
            author_stats[author]["prs_created"] += 1
            author_stats[author]["total_pr_size"] += (pr.additions or 0) + (pr.deletions or 0)
        
        for review in reviews:
            reviewer = review.reviewer.github_username
            pr_author = review.pull_request.author.github_username
            
            # Skip self-reviews
            if reviewer == pr_author:
                continue
            
            # Track reviewer stats
            if reviewer not in reviewer_stats:
                reviewer_stats[reviewer] = {
                    "name": review.reviewer.name,
                    "reviews_given": 0,
                    "unique_authors_reviewed": set(),
                    "avg_review_time_hours": 0,
                    "total_review_time": 0,
                    "review_times": []
                }
            
            reviewer_stats[reviewer]["reviews_given"] += 1
            reviewer_stats[reviewer]["unique_authors_reviewed"].add(pr_author)
            
            # Track review relationships (author -> reviewer)
            if pr_author not in review_relationships:
                review_relationships[pr_author] = {}
            
            if reviewer not in review_relationships[pr_author]:
                review_relationships[pr_author][reviewer] = {
                    "review_count": 0,
                    "total_review_time": 0,
                    "avg_review_time": 0
                }
            
            review_relationships[pr_author][reviewer]["review_count"] += 1
            
            # Calculate review time if available
            if review.created_at and review.pull_request.created_at:
                review_time = (review.created_at - review.pull_request.created_at).total_seconds() / 3600
                review_relationships[pr_author][reviewer]["total_review_time"] += review_time
                reviewer_stats[reviewer]["review_times"].append(review_time)
            
            # Update author stats
            if pr_author in author_stats:
                author_stats[pr_author]["total_reviews_received"] += 1
                author_stats[pr_author]["unique_reviewers"].add(reviewer)
        
        # Calculate averages and convert sets to counts
        for author, stats in author_stats.items():
            if stats["prs_created"] > 0:
                stats["avg_pr_size"] = stats["total_pr_size"] / stats["prs_created"]
            stats["unique_reviewers"] = len(stats["unique_reviewers"])
        
        for reviewer, stats in reviewer_stats.items():
            stats["unique_authors_reviewed"] = len(stats["unique_authors_reviewed"])
            if stats["review_times"]:
                stats["avg_review_time_hours"] = sum(stats["review_times"]) / len(stats["review_times"])
        
        # Calculate review time averages for relationships
        for author_reviews in review_relationships.values():
            for reviewer_data in author_reviews.values():
                if reviewer_data["review_count"] > 0:
                    reviewer_data["avg_review_time"] = reviewer_data["total_review_time"] / reviewer_data["review_count"]
        
        # Identify key patterns
        patterns = self._identify_influence_patterns(review_relationships, author_stats, reviewer_stats)
        
        return {
            "review_relationships": review_relationships,
            "author_stats": author_stats,
            "reviewer_stats": reviewer_stats,
            "patterns": patterns
        }
    
    def _identify_influence_patterns(
        self,
        review_relationships: Dict[str, Dict[str, Dict[str, Any]]],
        author_stats: Dict[str, Any],
        reviewer_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify key patterns in the influence map.
        
        Args:
            review_relationships: Author -> Reviewer -> metrics mapping
            author_stats: Author statistics
            reviewer_stats: Reviewer statistics
            
        Returns:
            Dictionary with identified patterns
        """
        # Find knowledge bottlenecks (reviewers who review for many authors)
        bottlenecks = []
        for reviewer, stats in reviewer_stats.items():
            if stats["unique_authors_reviewed"] >= 3 and stats["reviews_given"] >= 5:
                bottlenecks.append({
                    "reviewer": reviewer,
                    "authors_reviewed": stats["unique_authors_reviewed"],
                    "total_reviews": stats["reviews_given"],
                    "avg_review_time": stats["avg_review_time_hours"]
                })
        
        bottlenecks.sort(key=lambda x: x["authors_reviewed"], reverse=True)
        
        # Find isolated authors (authors with few reviewers)
        isolated_authors = []
        for author, stats in author_stats.items():
            if stats["prs_created"] >= 2 and stats["unique_reviewers"] <= 1:
                isolated_authors.append({
                    "author": author,
                    "prs_created": stats["prs_created"],
                    "unique_reviewers": stats["unique_reviewers"],
                    "avg_pr_size": stats["avg_pr_size"]
                })
        
        # Find review pairs (strong author-reviewer relationships)
        strong_pairs = []
        for author, reviewers in review_relationships.items():
            for reviewer, data in reviewers.items():
                if data["review_count"] >= 3:
                    strong_pairs.append({
                        "author": author,
                        "reviewer": reviewer,
                        "review_count": data["review_count"],
                        "avg_review_time": data["avg_review_time"]
                    })
        
        strong_pairs.sort(key=lambda x: x["review_count"], reverse=True)
        
        # Calculate overall collaboration metrics
        total_relationships = sum(len(reviewers) for reviewers in review_relationships.values())
        unique_reviewers = len(reviewer_stats)
        unique_authors = len(author_stats)
        
        collaboration_density = total_relationships / (unique_authors * unique_reviewers) if unique_authors > 0 and unique_reviewers > 0 else 0
        
        return {
            "bottlenecks": bottlenecks[:5],  # Top 5 bottlenecks
            "isolated_authors": isolated_authors,
            "strong_pairs": strong_pairs[:10],  # Top 10 pairs
            "collaboration_metrics": {
                "total_review_relationships": total_relationships,
                "unique_reviewers": unique_reviewers,
                "unique_authors": unique_authors,
                "collaboration_density": collaboration_density
            }
        }
    
    async def _analyze_influence_patterns(
        self,
        repository: Repository,
        influence_data: Dict[str, Any]
    ) -> str:
        """Get LLM analysis of influence patterns.
        
        Args:
            repository: Repository object
            influence_data: Influence map data
            
        Returns:
            String with influence analysis
        """
        patterns = influence_data["patterns"]
        
        prompt_template = """
        Repository: {repo_name}
        
        Code Review Influence Map Analysis:
        
        Collaboration Metrics:
        - Total Review Relationships: {total_relationships}
        - Unique Reviewers: {unique_reviewers}
        - Unique Authors: {unique_authors}
        - Collaboration Density: {collaboration_density:.2%}
        
        Knowledge Bottlenecks (Top Reviewers):
        {bottlenecks_section}
        
        Isolated Authors (Low Review Coverage):
        {isolated_authors_section}
        
        Strong Review Pairs:
        {strong_pairs_section}
        
        Based on this code review influence map, analyze:
        
        1. Knowledge Distribution:
           - Are there concerning knowledge bottlenecks?
           - Is review load distributed healthily across the team?
           - Which team members might be at risk of becoming single points of failure?
        
        2. Collaboration Patterns:
           - How well is the team collaborating on code reviews?
           - Are there silos or isolated developers who need more support?
           - What does the collaboration density suggest about team dynamics?
        
        3. Review Quality Risks:
           - Are there patterns that might indicate rushed or insufficient reviews?
           - Which relationships show healthy review practices vs. potential risks?
        
        4. Recommendations:
           - How can the team improve knowledge sharing and review distribution?
           - What specific actions would reduce bottlenecks and improve collaboration?
           - Are there mentoring or pairing opportunities suggested by the data?
        
        Focus on actionable insights that help improve team collaboration and knowledge sharing.
        """
        
        # Prepare sections
        bottlenecks_section = ""
        if patterns["bottlenecks"]:
            bottlenecks_lines = ["Top Knowledge Bottlenecks:"]
            for bottleneck in patterns["bottlenecks"]:
                bottlenecks_lines.append(
                    f"- {bottleneck['reviewer']}: reviews for {bottleneck['authors_reviewed']} authors, "
                    f"{bottleneck['total_reviews']} total reviews, "
                    f"avg {bottleneck['avg_review_time']:.1f}h response time"
                )
            bottlenecks_section = "\n".join(bottlenecks_lines)
        else:
            bottlenecks_section = "No significant knowledge bottlenecks identified."
        
        isolated_authors_section = ""
        if patterns["isolated_authors"]:
            isolated_lines = ["Authors with Limited Review Coverage:"]
            for author in patterns["isolated_authors"]:
                isolated_lines.append(
                    f"- {author['author']}: {author['prs_created']} PRs, "
                    f"only {author['unique_reviewers']} reviewer(s), "
                    f"avg PR size: {author['avg_pr_size']:.0f} lines"
                )
            isolated_authors_section = "\n".join(isolated_lines)
        else:
            isolated_authors_section = "All authors have adequate review coverage."
        
        strong_pairs_section = ""
        if patterns["strong_pairs"]:
            pairs_lines = ["Strongest Review Relationships:"]
            for pair in patterns["strong_pairs"][:5]:
                pairs_lines.append(
                    f"- {pair['author']} → {pair['reviewer']}: {pair['review_count']} reviews, "
                    f"avg {pair['avg_review_time']:.1f}h response time"
                )
            strong_pairs_section = "\n".join(pairs_lines)
        else:
            strong_pairs_section = "No strong review pairs identified."
        
        # Format the prompt
        prompt = prompt_template.format(
            repo_name=repository.full_name,
            total_relationships=patterns["collaboration_metrics"]["total_review_relationships"],
            unique_reviewers=patterns["collaboration_metrics"]["unique_reviewers"],
            unique_authors=patterns["collaboration_metrics"]["unique_authors"],
            collaboration_density=patterns["collaboration_metrics"]["collaboration_density"],
            bottlenecks_section=bottlenecks_section,
            isolated_authors_section=isolated_authors_section,
            strong_pairs_section=strong_pairs_section
        )
        
        # Create callback for logging
        callback = self.create_logger_callback("influence_map_analysis")
        
        # Get analysis from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate(
            [messages],
            callbacks=[callback]
        )
        
        return response.generations[0][0].text
