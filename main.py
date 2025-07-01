import os
import asyncio
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from agents.data_harvester import data_harvester_node
from agents.diff_analyst import diff_analyst_node
from agents.insight_narrator import insight_narrator_node
from agents.sample_data_harvester import sample_data_harvester
from agents.query_agent import create_query_agent
from langgraph.graph import StateGraph
from dotenv import load_dotenv
from typing import TypedDict, Dict, Any
import json
import concurrent.futures

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN, process_before_response=True)

class DevReportState(TypedDict):
    commits: list
    analysis: dict
    summary: str
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

@app.command("/dev-report")
def handle_dev_report_command(ack, body, respond, client: WebClient):
    ack()
    
    def process_report():
        try:
            channel_id = body["channel_id"]
            respond("📊 Generating your dev productivity report, please wait...")
            
            result = graph.invoke({})
            summary = result.get("summary", "No summary available.")
            
            channel_reports[channel_id] = result

            
            chunk_size = 3000
            for i in range(0, len(summary), chunk_size):
                chunk = summary[i:i+chunk_size]
                respond(chunk)
                
            respond("💡 You can now ask questions about this report using `/dev-ask [your question]`")

        except Exception as e:
            respond(f"❌ Error generating report: {str(e)}")
    
    thread = threading.Thread(target=process_report)
    thread.daemon = True  
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
    global executor
    if executor:
        executor.shutdown(wait=True)

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    try:
        SocketModeHandler(app, SLACK_APP_TOKEN).start()
    except KeyboardInterrupt:
        print("Shutting down...")
        cleanup()
    except Exception as e:
        print(f"Error starting bot: {e}")
        cleanup()