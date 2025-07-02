from typing import Dict, Any, List
from langchain.agents import Tool
from langchain.schema import BaseMessage, HumanMessage
from fika_db.database import fetch_commits, fetch_pull_requests

class DataHarvester:
    """
    LangChain agent responsible for fetching GitHub data (commits, PRs, etc.) and storing it in the database.
    """
    
    def __init__(self):
        self.name = "DataHarvester"
        self.description = "Fetches GitHub data including commits and pull requests from the database"
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch all GitHub data from the database"""
        commits = fetch_commits()
        prs = fetch_pull_requests()
        
        return {
            "commits": commits,
            "pull_requests": prs,
            "total_commits": len(commits),
            "total_prs": len(prs),
            "status": "success"
        }
    
    def get_tool(self) -> Tool:
        """Return a LangChain Tool for this agent"""
        return Tool(
            name="fetch_github_data",
            description="Fetches GitHub commits and pull request data from the database",
            func=lambda x: self.fetch_data()
        )
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message and return GitHub data"""
        return self.fetch_data() 