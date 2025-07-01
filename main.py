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
from typing import TypedDict, Dict, Any
import json
import concurrent.futures
import logging
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN, process_before_response=True)

class DevReportState(TypedDict):
    commits: list
    analysis: dict
    summary: str

builder = StateGraph(DevReportState)
builder.add_node("harvester", data_harvester_node)
builder.add_node("analyst", diff_analyst_node)
builder.add_node("narrator", insight_narrator_node)

builder.set_entry_point("harvester")
builder.add_edge("harvester", "analyst")
builder.add_edge("analyst", "narrator")
graph = builder.compile()

channel_reports: Dict[str, Dict[str, Any]] = {}
query_agent = create_query_agent()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Initialize chart generator
chart_generator = ChartGenerator()

def run_async_in_thread(coro):
    """Run a coroutine in a new thread with its own event loop"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            return result
        except Exception as e:
            print(f"Error in async thread: {e}")
            raise
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                loop.close()
    
    future = executor.submit(run)
    return future.result(timeout=60)

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
        if file_size > 20 * 1024 * 1024:  # Slack's file size limit is 20MB
            logger.error(f"Chart file too large: {file_size/1024/1024:.2f}MB")
            return False
            
        filename = os.path.basename(chart_path)
        
        try:
            # First try with files_upload_v2
            with open(chart_path, 'rb') as file_content:
                response = client.files_upload_v2(
                    channel=channel_id,  # Note: 'channel' instead of 'channels' in v2
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
            
            # Fallback to chat.postMessage with file upload
            try:
                with open(chart_path, 'rb') as file_content:
                    # Upload the file first
                    upload_response = client.files_upload_v2(
                        channels=channel_id,
                        file=file_content,
                        filename=filename,
                        title=title or "Development Metrics"
                    )
                    
                    if upload_response.get('ok', False):
                        # Get the file URL
                        file_info = upload_response['file']
                        file_url = file_info.get('url_private')
                        
                        # Post a message with the file
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
            
            # Generate the report using LangGraph
            result = graph.invoke({})
            summary = result.get("summary", "No summary available.")
            
            # Store the full result for potential follow-up questions
            channel_reports[channel_id] = result
            
            # Send the summary in chunks to avoid Slack's message length limits
            chunk_size = 3000
            for i in range(0, len(summary), chunk_size):
                chunk = summary[i:i+chunk_size]
                respond(chunk)
            
            # Generate and upload charts if we have commit data
            if 'commits' in result and result['commits']:
                respond("📈 Generating visualizations... (this may take a moment)")
                
                try:
                    # Clean up old charts
                    cleanup_temp_charts()
                    
                    # Generate all charts
                    chart_paths = []
                    chart_methods = [
                        (chart_generator.generate_commit_activity_chart, "commit_activity"),
                        (chart_generator.generate_author_contribution_chart, "author_contributions"),
                        (chart_generator.generate_file_activity_chart, "file_activity"),
                        (chart_generator.generate_hourly_commit_chart, "hourly_commits")
                    ]
                    
                    for method, chart_name in chart_methods:
                        try:
                            chart_path = method(result['commits'])
                            if chart_path and os.path.exists(chart_path):
                                chart_paths.append(chart_path)
                        except Exception as e:
                            logger.error(f"Error generating {chart_name} chart: {str(e)}")
                    
                    # Upload charts to Slack
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
                    
                    # Provide feedback on uploads
                    if successful_uploads > 0:
                        respond(f"✅ Successfully uploaded {successful_uploads} chart(s)!")
                    else:
                        respond("⚠️ Could not upload any charts. The text report is still available.")
                        
                except Exception as e:
                    logger.error(f"Error in chart generation/upload: {e}", exc_info=True)
                    respond("⚠️ There was an error generating some visualizations. The text report is still available.")
            
            # Let users know they can ask follow-up questions
            respond("💡 You can now ask questions about this report using `/dev-ask [your question]`")
            
        except Exception as e:
            logger.error(f"Error in handle_dev_report_command: {e}", exc_info=True)
            respond("❌ An error occurred while generating the report. Please try again later.")
    
    # Process the report in a separate thread to avoid blocking
    thread = threading.Thread(target=process_report)
    thread.daemon = True  # Allow the program to exit even if this thread is still running
    thread.start()

@app.command("/dev-ask")
def handle_dev_ask_command(ack, body, respond, client: WebClient):
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

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    # Ensure temp directory exists
    os.makedirs('temp_charts', exist_ok=True)
    
    # Start the app
    SocketModeHandler(
        app=app,
        app_token=os.environ["SLACK_APP_TOKEN"]
    ).start()