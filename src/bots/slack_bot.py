from slack_bolt import App
from slack_sdk import WebClient
import os
from dotenv import load_dotenv

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from main import build_graph

load_dotenv()

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# This gives us the raw client to send scheduled messages
client: WebClient = app.client

@app.command("/dev-report")
def handle_dev_report(ack, respond):
    ack()
    with open("src/storage/insight.txt") as f:
        summary = f.read()
    respond(summary)

def scheduled_job():
    print("🕒 Running scheduled Monday report...")
    graph = build_graph()
    graph.invoke({})

    try:
        with open("src/storage/insight.txt") as f:
            summary = f.read()
        client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL", "#general"),
            text=summary
        )
    except Exception as e:
        print(f"❌ Failed to send scheduled message: {e}")

# Schedule job for Monday 9 AM
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'cron', day_of_week='mon', hour=9, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3047)))
