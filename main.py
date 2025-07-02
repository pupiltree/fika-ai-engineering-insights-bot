import os
import asyncio
import threading
import shutil
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agents.data_harvester import data_harvester_node
from agents.diff_analyst import diff_analyst_node
from agents.insight_narrator import insight_narrator_node
from agents.sample_data_harvester import sample_data_harvester
from agents.query_agent import create_query_agent
from utils.chart_generator import ChartGenerator
from langgraph.graph import StateGraph
from dotenv import load_dotenv
from typing import TypedDict, Dict, Any, Optional
import json
import concurrent.futures
import logging
from pathlib import Path
from datetime import datetime

from database import (
    init_db,
    save_metrics,
    get_metrics,
    DBAccessError,
    SessionLocal
)

logger = logging.getLogger(__name__)

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN, process_before_response=True)

class DevReportState(TypedDict):
    commits: list
    analysis: dict
    summary: str
    repository: Optional[str] = None
    report_type: Optional[str] = "on-demand"
    pull_requests: Optional[list] = None

builder = StateGraph(DevReportState)
builder.add_node("harvester", sample_data_harvester)
builder.add_node("analyst", diff_analyst_node)
builder.add_node("narrator", insight_narrator_node)

builder.set_entry_point("harvester")
builder.add_edge("harvester", "analyst")
builder.add_edge("analyst", "narrator")
graph = builder.compile()

channel_reports: Dict[str, Dict[str, Any]] = {}
query_agent = create_query_agent()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

chart_generator = ChartGenerator()

def initialize_database():
    """Initialize the database connection"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.info("Continuing without database support")

initialize_database()

def store_metrics(repository: str, metrics: Dict[str, Any], report_type: str = "on-demand") -> None:
    """Store metrics in the database"""
    try:
        save_metrics(
            repository=repository,
            metrics=metrics,
            report_type=report_type
        )
        logger.info(f"Successfully stored metrics for {repository}")
    except DBAccessError as e:
        logger.error(f"Database error storing metrics: {e}")
    except Exception as e:
        logger.error(f"Unexpected error storing metrics: {e}")

def run_async_in_thread(coro, timeout: int = 300):
    """Run a coroutine in a new thread with its own event loop"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"Error in async thread: {e}", exc_info=True)
            raise
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as e:
                logger.error(f"Error during async cleanup: {e}")
            finally:
                loop.close()
    
    future = executor.submit(run)
    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        logger.error(f"Operation timed out after {timeout} seconds")
        future.cancel()
        raise TimeoutError(f"Operation timed out after {timeout} seconds. The report generation is taking longer than expected. Please try again later.")
    except Exception as e:
        logger.error(f"Error in run_async_in_thread: {e}", exc_info=True)
        raise

def cleanup_temp_charts():
    """Clean up temporary chart files."""
    try:
        temp_dir = Path('temp_charts')
        if temp_dir.exists() and temp_dir.is_dir():
            for file in temp_dir.glob('*.png'):
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Error deleting {file}: {e}")
    except Exception as e:
        logger.error(f"Error in cleanup_temp_charts: {e}")

def post_chart_to_slack(client: WebClient, channel_id: str, chart_path: str, title: str = None) -> bool:
    """
    Upload a chart to Slack using files_upload_v2.
    
    Args:
        client: Slack WebClient instance
        channel_id: ID of the channel to post to
        chart_path: Path to the chart image file
        title: Optional title for the file
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        if not os.path.exists(chart_path):
            logger.error(f"Chart file not found: {chart_path}")
            return False
            
        file_size = os.path.getsize(chart_path)
        if file_size > 20 * 1024 * 1024: 
            logger.error(f"Chart file too large: {file_size/1024/1024:.2f}MB")
            return False
            
        filename = os.path.basename(chart_path)
        
        try:
            with open(chart_path, 'rb') as file_content:
                response = client.files_upload_v2(
                    channel=channel_id,  
                    file=file_content,
                    title=title or "Development Metrics",
                    filename=filename,
                    initial_comment=title or "Development Metrics"
                )
                
            if response.get('ok', False):
                logger.info(f"Successfully uploaded {filename} to channel {channel_id}")
                return True
                
            logger.error(f"Upload failed: {response.get('error', 'Unknown error')}")
            return False
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            
            try:
                with open(chart_path, 'rb') as file_content:
                    upload_response = client.files_upload_v2(
                        channels=channel_id,
                        file=file_content,
                        filename=filename,
                        title=title or "Development Metrics"
                    )
                    
                    if upload_response.get('ok', False):
                        file_info = upload_response['file']
                        file_url = file_info.get('url_private')
                        
                        if file_url:
                            client.chat_postMessage(
                                channel=channel_id,
                                text=title or "Development Metrics",
                                blocks=[
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"*{title or 'Development Metrics'}*\nHere's your requested chart:"
                                        }
                                    },
                                    {
                                        "type": "image",
                                        "image_url": file_url,
                                        "alt_text": title or "Development Metrics"
                                    }
                                ]
                            )
                            return True
                        
            except Exception as fallback_error:
                logger.error(f"Fallback upload also failed: {str(fallback_error)}")
            
            return False
            
    except Exception as e:
        logger.error(f"Error in post_chart_to_slack: {str(e)}", exc_info=True)
        return False

@app.command("/dev-report")
def handle_dev_report_command(ack, body, respond, client: WebClient):
    """Handle the /dev-report slash command."""
    ack()
    
    def process_report():
        try:
            channel_id = body["channel_id"]
            respond("📊 Generating your dev productivity report, please wait...")
            
            state = {
                "commits": [],
                "analysis": {},
                "summary": "",
                "report_type": "on-demand"
            }
            
            result = run_async_in_thread(graph.ainvoke(state))
            
            if result and "analysis" in result:
                store_metrics(
                    repository="default_repo",
                    metrics=result["analysis"],
                    report_type=result.get("report_type", "on-demand")
                )
            
            channel_reports[channel_id] = result
            summary = result.get("summary", "No summary available.")
            
            chunk_size = 3000
            for i in range(0, len(summary), chunk_size):
                respond(summary[i:i+chunk_size])
            
            if 'commits' in result and result['commits']:
                respond("📈 Generating visualizations... (this may take a moment)")
                
                try:
                    cleanup_temp_charts()
                    
                    chart_paths = []
                    chart_methods = [
                        (chart_generator.generate_commit_activity_chart, "commit_activity"),
                        (chart_generator.generate_author_contribution_chart, "author_contributions"),
                        (chart_generator.generate_file_activity_chart, "file_activity"),
                        (chart_generator.generate_hourly_commit_chart, "hourly_commits")
                    ]
                    
                    # Generate standard charts from commits
                    for method, chart_name in chart_methods:
                        try:
                            chart_path = method(result['commits'])
                            if chart_path and os.path.exists(chart_path):
                                chart_paths.append(chart_path)
                                logger.info(f"✅ Generated chart: {os.path.basename(chart_path)}")
                            else:
                                logger.warning(f"⚠️ Failed to generate chart: {chart_name}")
                        except Exception as e:
                            logger.error(f"❌ Error generating {chart_name} chart: {str(e)}", exc_info=True)
                    
                    # Generate review influence map if pull request data is available
                    pr_data = result.get('pull_requests', [])
                    logger.info(f"Found {len(pr_data)} pull requests in the result")
                    
                    if pr_data:
                        logger.info(f"Sample PR data: {json.dumps(pr_data[0], indent=2)}")
                        try:
                            logger.info("Attempting to generate review influence map...")
                            chart_path = chart_generator.generate_review_influence_map(pr_data)
                            if chart_path and os.path.exists(chart_path):
                                chart_paths.append(chart_path)
                                logger.info(f"✅ Successfully generated review influence map: {chart_path}")
                            else:
                                logger.warning("⚠️ Failed to generate review influence map: No valid data or file not created")
                                if not pr_data:
                                    logger.warning("⚠️ No pull request data available")
                                else:
                                    logger.warning(f"⚠️ PR data exists but chart generation failed. First PR: {pr_data[0]}")
                        except Exception as e:
                            logger.error(f"❌ Error generating review influence map: {str(e)}", exc_info=True)
                    else:
                        logger.warning("⚠️ No pull request data found in the result")
                    
                    successful_uploads = 0
                    for chart_path in chart_paths:
                        if os.path.exists(chart_path):
                            upload_result = post_chart_to_slack(
                                client, 
                                channel_id, 
                                chart_path,
                                title=f"Dev Report - {os.path.basename(chart_path).replace('.png', '')}"
                            )
                            if upload_result:
                                successful_uploads += 1
                    
                    if successful_uploads > 0:
                        respond(f"✅ Successfully uploaded {successful_uploads} chart(s)!")
                    else:
                        respond("⚠️ Could not upload any charts. The text report is still available.")
                            
                except Exception as e:
                    logger.error(f"Error in chart generation/upload: {e}", exc_info=True)
                    respond("⚠️ There was an error generating some visualizations. The text report is still available.")
            
            respond("💡 You can now ask questions about this report using `/dev-ask [your question]`")
            
        except Exception as e:
            logger.error(f"Error in handle_dev_report_command: {e}", exc_info=True)
            respond("❌ An error occurred while generating the report. Please try again later.")
    
    thread = threading.Thread(target=process_report)
    thread.daemon = True  
    thread.start()

@app.command("/dev-ask")
def handle_dev_ask_command(ack, body, respond, client: WebClient):
    """Handle the /dev-ask slash command."""
    ack()
    
    def process_question():
        try:
            channel_id = body["channel_id"]
            question = body.get("text", "").strip()
            
            if not question:
                respond("Please provide a question. Example: `/dev-ask Who made the most commits last month?`")
                return
            
            respond(f"🤔 Processing your question: *{question}*")
            
            report_data = channel_reports.get(channel_id)
            
            if not report_data:
                respond("No report data found for this channel. Please generate a report first with `/dev-report`")
                return
            
            try:
                answer = query_agent.query(question, report_data)
                respond(f"🔍 *Question:* {question}\n\n{answer}")
            except Exception as e:
                respond(f"❌ Error processing your question: {str(e)}")
            
        except Exception as e:
            respond(f"❌ Error: {str(e)}")
    
    thread = threading.Thread(target=process_question)
    thread.daemon = True  
    thread.start()

def cleanup():
    """Cleanup function to be called on exit"""
    cleanup_temp_charts()
    executor.shutdown(wait=False)
    
    
    async def close_db():
        from database import engine
        if engine:
            await engine.dispose()
    
    try:
        run_async_in_thread(close_db())
    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    os.makedirs('temp_charts', exist_ok=True)
    
    SocketModeHandler(
        app=app,
        app_token=os.environ["SLACK_APP_TOKEN"]
    ).start()