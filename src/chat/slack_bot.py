"""Slack bot for engineering productivity reports."""
import re
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from ..config import settings, logger
from ..graph.workflow import run_productivity_analysis
from ..graph.state import WorkflowState
from .formatters import format_slack_report


class ProductivitySlackBot:
    """Slack bot for handling /dev-report commands."""
    
    def __init__(self):
        self.app = App(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret
        )
        self._setup_handlers()
        logger.info("Slack bot initialized")
    
    def _setup_handlers(self):
        """Set up Slack event handlers."""
        
        @self.app.command("/dev-report")
        def handle_dev_report_command(ack, command, respond):
            """Handle /dev-report slash command."""
            # Acknowledge the command immediately (must be within 3 seconds)
            ack()
            
            try:
                # Parse command parameters
                params = self._parse_command_params(command.get("text", ""))
                
                # Add channel info for file uploads
                params['channel_id'] = command.get('channel_id')
                params['user_id'] = command.get('user_id')
                
                # Send immediate response
                respond({
                    "response_type": "in_channel",
                    "text": f"🔄 Generating productivity report for `{params['repo_name']}`...\n"
                           f"📅 Period: {params['period_start'].strftime('%Y-%m-%d')} to {params['period_end'].strftime('%Y-%m-%d')}\n"
                           f"⏱️ This may take 30-60 seconds..."
                })
                
                # Run the analysis workflow
                logger.info(f"Starting analysis for user {command['user_id']}")
                final_state = run_productivity_analysis(
                    repo_name=params["repo_name"],
                    period_start=params["period_start"],
                    period_end=params["period_end"],
                    requested_by=command["user_id"],
                    command_params=params
                )
                
                # Format and send the results
                if final_state.get("completed_at") and not final_state.get("errors"):
                    self._send_success_report(respond, final_state, params)
                else:
                    self._send_error_report(respond, final_state)
                    
            except Exception as e:
                logger.error(f"Command handling failed: {e}")
                respond({
                    "response_type": "ephemeral",
                    "text": f"❌ Sorry, something went wrong: {str(e)}\n"
                           f"Please try again or contact support."
                })
        
        @self.app.event("app_mention")
        def handle_mention(event, say):
            """Handle @bot mentions."""
            say(f"👋 Hi <@{event['user']}>! Use `/dev-report` to get productivity insights.")
        
        @self.app.event("message")
        def handle_message_events(body, logger):
            """Handle message events (required for some Slack setups)."""
            pass
    
    def _parse_command_params(self, text: str) -> Dict[str, Any]:
        """Parse slash command parameters."""
        # Default values
        period_type = "weekly"
        repo_name = f"{settings.default_repo_owner}/{settings.default_repo_name}"
        author = None
        
        # Parse text parameters
        if text:
            tokens = text.strip().split()
            
            # First token might be period type
            if tokens and tokens[0].lower() in ["daily", "weekly", "monthly"]:
                period_type = tokens[0].lower()
                tokens = tokens[1:]
            
            # Next token might be repo name
            if tokens:
                if "/" in tokens[0]:  # Looks like owner/repo
                    repo_name = tokens[0]
                    tokens = tokens[1:]
                elif len(tokens) >= 2:  # owner repo (separate tokens)
                    repo_name = f"{tokens[0]}/{tokens[1]}"
                    tokens = tokens[2:]
            
            # Remaining token might be author
            if tokens:
                author = tokens[0]
        
        # Calculate date range based on period type
        end_date = datetime.now()
        if period_type == "daily":
            start_date = end_date - timedelta(days=1)
        elif period_type == "monthly":
            start_date = end_date - timedelta(days=30)
        else:  # weekly (default)
            start_date = end_date - timedelta(days=7)
        
        return {
            "period_type": period_type,
            "repo_name": repo_name,
            "author": author,
            "period_start": start_date,
            "period_end": end_date,
            "original_text": text
        }
    
    def _send_success_report(self, respond, final_state: WorkflowState, params: Dict[str, Any]):
        """Send successful analysis report to Slack."""
        try:
            # Format the report for Slack
            slack_report = format_slack_report(final_state, params)
            
            # Create rich Slack message with better structure
            blocks = [
                # Main Header
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 {slack_report.title}"
                    }
                },
                
                # Executive Summary Section
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🎯 Executive Summary*\n{slack_report.summary}"
                    }
                },
                
                {
                    "type": "divider"
                },
                
                # Key Metrics in a clean format
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*👥 Contributors*\n{len(final_state.get('diff_stats', []))}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*📝 Events*\n{final_state.get('events_count', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*⏱️ Processing Time*\n{final_state.get('processing_time_ms', 0) / 1000:.1f}s"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*📅 Period*\n{params['period_start'].strftime('%m/%d')} - {params['period_end'].strftime('%m/%d')}"
                        }
                    ]
                },
                
                {
                    "type": "divider"
                }
            ]
            
            # DORA Metrics Section (if available)
            dora = final_state.get("dora_metrics")
            if dora:
                dora_fields = []
                if dora.deployment_frequency is not None:
                    dora_fields.append({
                        "type": "mrkdwn",
                        "text": f"*🚀 Deploy Frequency*\n{dora.deployment_frequency:.2f}/day"
                    })
                if dora.lead_time_hours is not None:
                    dora_fields.append({
                        "type": "mrkdwn",
                        "text": f"*⏱️ Lead Time*\n{dora.lead_time_hours:.1f} hours"
                    })
                if dora.change_failure_rate is not None:
                    dora_fields.append({
                        "type": "mrkdwn",
                        "text": f"*❌ Failure Rate*\n{dora.change_failure_rate:.1%}"
                    })
                if dora.mttr_hours is not None:
                    dora_fields.append({
                        "type": "mrkdwn",
                        "text": f"*🔧 MTTR*\n{dora.mttr_hours:.1f} hours"
                    })
                
                if dora_fields:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*📊 DORA Four Key Metrics*"
                        }
                    })
                    blocks.append({
                        "type": "section",
                        "fields": dora_fields
                    })
                    blocks.append({"type": "divider"})
            
            # Top Contributors Section
            diff_stats = final_state.get("diff_stats", [])
            if diff_stats:
                top_3_contributors = sorted(diff_stats, key=lambda s: s.commit_count, reverse=True)[:3]
                contrib_text = "*🏆 Top Contributors*\n"
                for i, stat in enumerate(top_3_contributors, 1):
                    contrib_text += f"`{i}.` **{stat.author}** - {stat.commit_count} commits, {stat.total_additions + stat.total_deletions:,} lines\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": contrib_text
                    }
                })
                blocks.append({"type": "divider"})
            
            # AI Insights Section
            narrative = final_state.get("narrative", "")
            if narrative:
                # Clean up the narrative - remove markdown headers and truncate
                clean_narrative = narrative.replace("##", "").replace("#", "").strip()
                if len(clean_narrative) > 400:
                    clean_narrative = clean_narrative[:400] + "..."
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🧠 AI Analysis*\n{clean_narrative}"
                    }
                })
                blocks.append({"type": "divider"})
            
            # Actionable Insights Section
            insights = final_state.get("actionable_insights", [])
            if insights:
                insights_text = "*🎯 Recommended Actions*\n"
                for i, insight in enumerate(insights[:3], 1):
                    # Clean up the insight text
                    clean_insight = insight.strip().lstrip('•').lstrip('*').strip()
                    insights_text += f"`{i}.` {clean_insight}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": insights_text
                    }
                })
                blocks.append({"type": "divider"})
            
            # Detailed Metrics Table (Collapsible)
            if slack_report.metrics_table:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📈 Detailed Metrics*"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "action_id": "view_metrics"
                    }
                })
                
                # Add metrics in a code block (but smaller)
                clean_table = slack_report.metrics_table[:800]  # Truncate if too long
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{clean_table}```"
                    }
                })
            
            # Footer
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 *Powered by AI agents* | 📈 Charts will be uploaded separately"
                    }
                ]
            })
            
            # Send the main report
            respond({
                "response_type": "in_channel",
                "blocks": blocks
            })
            
            # Upload charts as files to Slack
            charts = final_state.get("charts", [])
            if charts:
                self._upload_charts_to_slack(charts, params)
            
            logger.info("Successfully sent productivity report to Slack")
            
        except Exception as e:
            logger.error(f"Failed to send success report: {e}")
            respond({
                "response_type": "ephemeral", 
                "text": f"✅ Analysis completed, but formatting failed: {str(e)}"
            })
    
    def _upload_charts_to_slack(self, chart_paths: list, params: Dict[str, Any]):
        """Upload chart files to Slack."""
        try:
            from slack_sdk import WebClient
            
            # Create a WebClient for file uploads
            client = WebClient(token=settings.slack_bot_token)
            
            # Get channel from the command context
            channel = params.get('channel_id', 'general')
            
            logger.info(f"Attempting to upload {len(chart_paths)} charts to channel {channel}")
            
            for chart_path in chart_paths:
                try:
                    # Check if file exists
                    if not os.path.exists(chart_path):
                        logger.error(f"Chart file does not exist: {chart_path}")
                        continue
                    
                    # Get chart filename for title
                    chart_name = chart_path.split('\\')[-1] if '\\' in chart_path else chart_path.split('/')[-1]
                    chart_title = chart_name.replace('.png', '').replace('_', ' ').title()
                    
                    logger.info(f"Uploading chart: {chart_name} to channel {channel}")
                    
                    # Try to join the channel first (if we have permission)
                    try:
                        client.conversations_join(channel=channel)
                    except Exception as join_error:
                        logger.warning(f"Could not join channel {channel}: {join_error}")
                    
                    # Upload file to Slack using files_upload
                    with open(chart_path, 'rb') as file_content:
                        response = client.files_upload_v2(
                            channel=channel,
                            file=file_content,
                            title=f"📊 {chart_title}",
                            initial_comment=f"**{chart_title}** - Generated from productivity analysis"
                        )
                    
                    if response["ok"]:
                        logger.info(f"Successfully uploaded chart: {chart_name}")
                    else:
                        logger.error(f"Failed to upload chart {chart_name}: {response.get('error', 'Unknown error')}")
                        
                except Exception as upload_error:
                    logger.error(f"Error uploading chart {chart_path}: {upload_error}")
                    
        except Exception as e:
            logger.error(f"Failed to upload charts to Slack: {e}")
            # Don't fail the entire process if chart upload fails
    
    def _send_error_report(self, respond, final_state: WorkflowState):
        """Send error report to Slack."""
        errors = final_state.get("errors", ["Unknown error"])
        warnings = final_state.get("warnings", [])
        
        error_text = f"❌ **Analysis Failed**\n\n"
        error_text += f"**Errors:**\n"
        for error in errors[:3]:  # Show max 3 errors
            error_text += f"• {error}\n"
        
        if warnings:
            error_text += f"\n**Warnings:**\n"
            for warning in warnings[:2]:  # Show max 2 warnings
                error_text += f"• {warning}\n"
        
        error_text += f"\n💡 **Troubleshooting:**\n"
        error_text += f"• Check if the repository exists and is accessible\n"
        error_text += f"• Verify GitHub token has proper permissions\n"
        error_text += f"• Try a different date range or repository"
        
        respond({
            "response_type": "ephemeral",
            "text": error_text
        })
        
        logger.warning(f"Sent error report to Slack: {errors}")
    
    def start_socket_mode(self):
        """Start the bot in Socket Mode (for development)."""
        if not settings.slack_app_token:
            logger.error("SLACK_APP_TOKEN not found - Socket Mode requires app-level token")
            return
        
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        handler = SocketModeHandler(self.app, settings.slack_app_token)
        logger.info("Starting Slack bot in Socket Mode...")
        handler.start()
    
    def start_http_mode(self, port: int = 3000):
        """Start the bot in HTTP mode (for production)."""
        logger.info(f"Starting Slack bot in HTTP mode on port {port}")
        self.app.start(port=port)
    
    def get_app(self):
        """Get the Slack app instance (for external WSGI servers)."""
        return self.app


# Global bot instance
productivity_bot = ProductivitySlackBot()


def start_slack_bot(mode: str = "auto", port: int = 3000):
    """Start the Slack bot in the specified mode."""
    if mode == "auto":
        # Auto-detect based on available tokens
        if settings.slack_app_token:
            logger.info("SLACK_APP_TOKEN found - using Socket Mode")
            productivity_bot.start_socket_mode()
        else:
            logger.info("No SLACK_APP_TOKEN - using HTTP Mode")
            productivity_bot.start_http_mode(port)
    elif mode == "socket":
        productivity_bot.start_socket_mode()
    else:
        productivity_bot.start_http_mode(port)


if __name__ == "__main__":
    # For local development
    start_slack_bot("http", 3000)