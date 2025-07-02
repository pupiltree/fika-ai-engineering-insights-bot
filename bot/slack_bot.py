import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

"""
Slack bot entry point. Handles slash commands and posts reports to Slack channels.
"""

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from fika_agents.workflow import FikaWorkflow
from fika_db import database

# Load Slack bot token and app token from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

def get_weekly_report():
    database.init_db()
    workflow = FikaWorkflow()
    summary = workflow.run_weekly_report()
    return summary

@app.command("/dev-report")
def handle_dev_report(ack, respond, command):
    ack()
    text = command.get("text", "").strip()
    if text == "weekly":
        summary = get_weekly_report()
        respond(f"*Weekly Engineering Productivity Report (LangGraph):*\n```{summary}```")
    else:
        respond("Usage: `/dev-report weekly`")

@app.command("/test")
def handle_test(ack, respond):
    ack()
    respond("Bot is working! 🎉")

@app.event("app_mention")
def handle_mention(event, say):
    say("Hello! I'm the FIKA AI bot. Use `/dev-report weekly` to get insights!")

if __name__ == "__main__":
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        print("Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables.")
    else:
        print("Starting Slack bot with LangGraph workflow...")
        SocketModeHandler(app, SLACK_APP_TOKEN).start() 