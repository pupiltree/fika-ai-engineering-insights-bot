"""
Slack Bot integration for PowerBiz
"""

import os
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from powerbiz.agents.workflow import EngineeringReportWorkflow
from powerbiz.visualization.reports import (
    generate_daily_report_blocks,
    generate_weekly_report_blocks
)
from powerbiz.database.db import get_session, init_db
from powerbiz.database.models import Repository

logger = logging.getLogger(__name__)

# Demo mode for testing without real API keys
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

class SlackBot:
    """Slack Bot for delivering engineering insights."""
    
    def __init__(self):
        """Initialize the Slack bot."""
        self.app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
        )
        
        self.workflow = EngineeringReportWorkflow()
        
        # Register event handlers
        self._register_handlers()
        
        # Initialize database
        init_db()
    
    def _register_handlers(self):
        """Register Slack event handlers."""
        # Register slash command handler
        self.app.command("/dev-report")(self.handle_dev_report_command)
        
        # Register message handlers
        self.app.message("help")(self.handle_help_message)
        self.app.message(re.compile(".*"))(self.handle_fallback_message)
    
    async def handle_dev_report_command(self, ack, command, say):
        """Handle the /dev-report slash command.
        
        Args:
            ack: Acknowledgment function
            command: Command data
            say: Function to send a message
        """
        # Acknowledge the command
        await ack()
        
        # Parse command text
        text = command["text"]
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        
        # Send thinking message
        thinking_msg = await say({
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":thinking_face: Generating your engineering report... This might take a minute."
                    }
                }
            ]
        })
        
        try:
            # Parse command to determine report type and repository
            report_type, repository_name, date = self._parse_command(text)
            
            if DEMO_MODE or not repository_name:
                # Generate demo report
                report_data = await self._generate_demo_report(report_type, repository_name)
            else:
                # Look up repository in database
                repository = await self._get_repository(repository_name)
                
                if not repository:
                    # Fallback to demo data if repository not found
                    report_data = await self._generate_demo_report(report_type, repository_name)
                else:
                    # Generate the report
                    report_state = await self.workflow.run_report_workflow(
                        repository.id,
                        report_type,
                        date
                    )
                    
                    # Check for errors and fallback to demo if needed
                    if report_state.get("error"):
                        report_data = await self._generate_demo_report(report_type, repository_name)
                    else:
                        report_data = report_state["narrative"]
            
            # Generate Slack blocks based on report type
            if report_type == "daily":
                blocks = generate_daily_report_blocks(report_data)
            elif report_type == "weekly":
                blocks = generate_weekly_report_blocks(report_data)
            else:
                blocks = generate_daily_report_blocks(report_data)  # Default to daily format
            
            # Update the message with the report
            await self.app.client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],
                blocks=blocks
            )
        
        except Exception as e:
            logger.exception("Error handling dev-report command")
            
            # Update the message with the error
            await self.app.client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Error generating report: {str(e)}"
                    }
                }]
            )
    
    async def handle_help_message(self, message, say):
        """Handle help message.
        
        Args:
            message: Message data
            say: Function to send a message
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "PowerBiz Developer Analytics Help",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Here's how to use the PowerBiz Developer Analytics bot:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Commands:*\n"
                           "• `/dev-report daily [repository]` - Get a daily engineering report\n"
                           "• `/dev-report weekly [repository]` - Get a weekly engineering report\n"
                           "• `/dev-report daily [repository] [YYYY-MM-DD]` - Get a report for a specific date\n"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Examples:*\n"
                           "• `/dev-report daily owner/repo` - Today's report for owner/repo\n"
                           "• `/dev-report weekly owner/repo` - Weekly report for owner/repo\n"
                           "• `/dev-report daily owner/repo 2023-07-01` - Daily report for a specific date\n"
                }
            }
        ]
        
        await say(blocks=blocks)
    
    async def handle_fallback_message(self, message, say):
        """Handle fallback messages (catch-all).
        
        Args:
            message: Message data
            say: Function to send a message
        """
        # Only respond to direct mentions or DMs
        if message.get("channel_type") == "im" or self.app.client.auth_test()["user_id"] in message.get("text", ""):
            await say({
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Hi! I'm the PowerBiz Developer Analytics bot. Use `/dev-report` to get engineering insights, or say 'help' for more information."
                        }
                    }
                ]
            })
    
    def _parse_command(self, text: str) -> tuple:
        """Parse the command text to extract parameters.
        
        Args:
            text: Command text
            
        Returns:
            Tuple of (report_type, repository_name, date)
        """
        parts = text.strip().split()
        
        # Default values
        report_type = "daily"
        repository_name = None
        date = None
        
        # Parse report type
        if parts and parts[0].lower() in ["daily", "weekly", "monthly"]:
            report_type = parts[0].lower()
        
        # Parse repository name
        if len(parts) > 1:
            repository_name = parts[1]
        
        # Parse date if provided
        if len(parts) > 2:
            date_str = parts[2]
            try:
                # Validate date format
                datetime.strptime(date_str, "%Y-%m-%d")
                date = date_str
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
        
        return report_type, repository_name, date
    
    async def _get_repository(self, repository_name: str) -> Optional[Repository]:
        """Get repository from database.
        
        Args:
            repository_name: Repository name (owner/repo)
            
        Returns:
            Repository object if found, None otherwise
        """
        if not repository_name:
            # Get the first repository in the database
            session = get_session()
            try:
                return session.query(Repository).first()
            finally:
                session.close()
        
        session = get_session()
        try:
            return session.query(Repository).filter_by(full_name=repository_name).first()
        finally:
            session.close()
    
    async def _generate_demo_report(self, report_type: str, repository_name: str) -> Dict[str, Any]:
        """Generate a demo report for testing without real data.
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            repository_name: Repository name
            
        Returns:
            Mock report data
        """
        return {
            "repository": {"full_name": repository_name or "demo/repository"},
            "date": datetime.now().strftime("%Y-%m-%d"),
            "metrics": {
                "commit_count": 15,
                "pr_count": 5,
                "cycle_time_hours": 24.5,
                "churn_score": 0.7
            },
            "narrative": {
                "sections": {
                    "overview": f"Demo {report_type} report for {repository_name or 'demo repository'}. The team made 15 commits and 5 pull requests. Average cycle time is 24.5 hours.",
                    "highlights": "Strong collaboration patterns observed. Code review coverage at 95%.",
                    "concerns": "One large PR detected that may need additional review.",
                    "recommendations": "Consider breaking down large features into smaller PRs."
                }
            }
        }
    
    def start(self):
        """Start the Slack bot."""
        # Start the Socket Mode handler
        handler = SocketModeHandler(self.app, os.environ.get("SLACK_APP_TOKEN"))
        handler.start()


def start_slack_bot():
    """Start the Slack bot."""
    # Check for required environment variables
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set all required environment variables.")
        return
    
    # Start the bot
    bot = SlackBot()
    bot.start()
