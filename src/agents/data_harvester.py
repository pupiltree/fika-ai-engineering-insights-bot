"""Data Harvester Agent - Fetches and processes GitHub events."""
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .base import BaseAgent, AgentError
from ..data.github_client import github_client
from ..data.database import db
from ..data.models import GitHubEvent, EventType
from ..graph.state import WorkflowState
from ..config import logger, settings


class DataHarvesterAgent(BaseAgent):
    """Agent responsible for harvesting GitHub data and storing it in the database."""
    
    def __init__(self):
        super().__init__(
            name="DataHarvester",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """You are a Data Harvester Agent specialized in analyzing GitHub repository activity.

Your role is to:
1. Assess the quality and completeness of fetched GitHub data
2. Identify any data gaps or anomalies in the collected events
3. Provide insights on data coverage and reliability
4. Suggest data collection improvements if needed

You should analyze:
- Event distribution (commits, PRs, reviews)
- Author activity patterns
- Time coverage and gaps
- Data quality indicators

Respond in a structured format focusing on data quality assessment and any recommendations for the analysis pipeline."""
    
    def process(self, state: WorkflowState) -> WorkflowState:
        """Process GitHub data harvesting for the given state."""
        logger.info(f"Starting data harvesting for {state['repo_name']}")
        
        try:
            # Extract repository information
            repo_name = state["repo_name"]
            owner, repo = self._parse_repo_name(repo_name)
            
            # First, try to get events from database (seeded data)
            events = db.get_github_events(
                repo_name, 
                state["period_start"], 
                state["period_end"]
            )
            
            # If no events in database, fetch from GitHub API
            if not events:
                logger.info("No events in database, fetching from GitHub API...")
                events = self._fetch_github_events(
                    owner, repo, 
                    state["period_start"], 
                    state["period_end"]
                )
                
                # Store fetched events in database
                stored_count = self._store_events(events)
            else:
                logger.info(f"Using {len(events)} events from database")
            
            # Analyze data quality
            quality_assessment = self._assess_data_quality(events, state)
            
            # Update state with results
            state["github_events"] = events
            state["events_count"] = len(events)
            state["data_quality_score"] = quality_assessment["quality_score"]
            
            # Add any warnings about data quality
            if quality_assessment["warnings"]:
                state["warnings"].extend(quality_assessment["warnings"])
            
            # Store agent-specific data
            state["agent_data"]["data_harvester"] = {
                "events_fetched": len(events),
                "events_stored": len(events),
                "quality_assessment": quality_assessment,
                "fetch_timestamp": datetime.now().isoformat(),
                "data_source": "database" if events else "github_api"
            }
            
            logger.info(f"Data harvesting completed: {len(events)} events, quality score: {quality_assessment['quality_score']:.2f}")
            return state
            
        except Exception as e:
            error_msg = f"Data harvesting failed: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            raise AgentError("DataHarvester", error_msg, e)
    
    def _parse_repo_name(self, repo_name: str) -> tuple[str, str]:
        """Parse repository name into owner and repo components."""
        if "/" in repo_name:
            parts = repo_name.split("/")
            return parts[0], parts[1]
        else:
            # Assume default owner if not specified
            return settings.default_repo_owner, repo_name
    
    def _fetch_github_events(
        self, 
        owner: str, 
        repo: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[GitHubEvent]:
        """Fetch GitHub events using the GitHub client."""
        try:
            # Test connection first
            if not github_client.test_connection():
                raise AgentError("DataHarvester", "GitHub API connection failed")
            
            # Fetch all repository events
            events = github_client.get_repository_events(
                owner=owner,
                repo=repo,
                since=start_date,
                until=end_date,
                include_prs=True,
                include_commits=True
            )
            
            logger.info(f"Fetched {len(events)} events from GitHub API")
            return events
            
        except Exception as e:
            raise AgentError("DataHarvester", f"Failed to fetch GitHub events: {str(e)}", e)
    
    def _store_events(self, events: List[GitHubEvent]) -> int:
        """Store events in the database."""
        stored_count = 0
        
        for event in events:
            try:
                if db.insert_github_event(event):
                    stored_count += 1
            except Exception as e:
                logger.warning(f"Failed to store event {event.id}: {e}")
        
        logger.info(f"Stored {stored_count}/{len(events)} events in database")
        return stored_count
    
    def _assess_data_quality(self, events: List[GitHubEvent], state: WorkflowState) -> Dict[str, Any]:
        """Assess the quality and completeness of the fetched data."""
        if not events:
            return {
                "quality_score": 0.0,
                "warnings": ["No events found for the specified period"],
                "assessment": "No data available",
                "recommendations": ["Check repository activity", "Verify date range", "Confirm repository access"]
            }
        
        # Analyze event distribution
        event_types = {}
        authors = set()
        dates = []
        
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            authors.add(event.author)
            dates.append(event.timestamp)
        
        # Calculate quality metrics
        quality_factors = []
        warnings = []
        recommendations = []
        
        # 1. Event variety (commits, PRs, reviews)
        event_variety_score = len(event_types) / 3.0  # Max 3 types
        quality_factors.append(event_variety_score)
        
        if EventType.COMMIT not in event_types:
            warnings.append("No commit events found")
            recommendations.append("Verify commit access permissions")
        
        if EventType.PULL_REQUEST not in event_types:
            warnings.append("No pull request events found")
        
        # 2. Author diversity
        author_diversity_score = min(len(authors) / 5.0, 1.0)  # Normalize to max 5 authors
        quality_factors.append(author_diversity_score)
        
        if len(authors) == 1:
            warnings.append("Only one author found - limited diversity")
        
        # 3. Time coverage
        if dates:
            date_range = (max(dates) - min(dates)).days
            expected_range = (state["period_end"] - state["period_start"]).days
            time_coverage_score = min(date_range / expected_range, 1.0) if expected_range > 0 else 1.0
            quality_factors.append(time_coverage_score)
            
            if time_coverage_score < 0.5:
                warnings.append("Limited time coverage in the data")
        
        # 4. Data completeness (events with diff stats)
        events_with_stats = sum(1 for e in events if e.additions is not None or e.deletions is not None)
        completeness_score = events_with_stats / len(events) if events else 0
        quality_factors.append(completeness_score)
        
        if completeness_score < 0.8:
            warnings.append("Some events missing diff statistics")
            recommendations.append("Check API permissions for detailed commit data")
        
        # Calculate overall quality score
        overall_quality = sum(quality_factors) / len(quality_factors)
        
        # Generate AI assessment
        ai_assessment = self._generate_ai_assessment(events, event_types, authors, overall_quality)
        
        return {
            "quality_score": overall_quality,
            "warnings": warnings,
            "recommendations": recommendations,
            "assessment": ai_assessment,
            "metrics": {
                "total_events": len(events),
                "event_types": event_types,
                "unique_authors": len(authors),
                "date_range_days": date_range if dates else 0,
                "completeness_score": completeness_score
            }
        }
    
    def _generate_ai_assessment(
        self, 
        events: List[GitHubEvent], 
        event_types: Dict[str, int], 
        authors: set,
        quality_score: float
    ) -> str:
        """Generate AI-powered assessment of the data quality."""
        
        # Prepare context for the LLM
        context = {
            "total_events": len(events),
            "event_breakdown": event_types,
            "author_count": len(authors),
            "authors": list(authors)[:10],  # Limit to first 10 authors
            "quality_score": f"{quality_score:.2f}",
            "sample_events": self._format_data_for_prompt(events[:5])  # Sample events
        }
        
        prompt = """Analyze this GitHub repository data collection:

Total Events: {total_events}
Event Types: {event_breakdown}
Authors ({author_count}): {authors}
Quality Score: {quality_score}/1.0

Sample Events:
{sample_events}

Provide a brief assessment of:
1. Data collection completeness
2. Repository activity patterns
3. Team collaboration indicators
4. Any notable patterns or concerns

Keep the response concise (2-3 sentences) and focus on actionable insights for productivity analysis."""
        
        try:
            assessment = self._invoke_llm(prompt, context)
            return assessment.strip()
        except Exception as e:
            logger.warning(f"Failed to generate AI assessment: {e}")
            return f"Data collection completed with {len(events)} events across {len(event_types)} event types from {len(authors)} authors."


# Global instance
data_harvester = DataHarvesterAgent()