# slack_bot.py

import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sys

# Ensure this module exists and provides seed data    

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


from main import run_pipeline  # Make sure main.py is in root and defines `run_pipeline`

# Initialize Slack app with Bot Token
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.command("/dev-report-weekly")
def weekly_report(ack, respond, command):
    ack()
    respond("Generating *weekly* report for your team...")
    run_pipeline(timeframe="weekly")
    _respond_with_report(respond)
    # Send charts after report
    channel = command['channel_id']
    chart_files = [
        ("output/commits_over_time.png", "Commits Over Time"),
        ("output/risky_vs_safe.png", "Risky vs Safe Commits"),
        ("output/churn_analysis.png", "Churn Analysis"),
        ("output/dora_metrics.png", "DORA Metrics"),
        ("output/pr_review.png", "PR Review Latency"),
    ]
    for file_path, title in chart_files:
        if os.path.exists(file_path):
            send_chart_to_slack(channel, file_path, title)
        else:
            respond(f"Chart not found: {file_path}")

@app.command("/daily-report")
def daily_report(ack, respond, command):
    ack()
    respond("Generating *daily* insights...")
    run_pipeline(timeframe="daily")
    _respond_with_report(respond)

@app.command("/dev-monthly-report")
def monthly_report(ack, respond, command):
    ack()
    respond("Generating *monthly* report for your team...")
    run_pipeline(timeframe="monthly")
    _respond_with_report(respond)

@app.command("/monthly-summary")
def monthly_summary(ack, respond, command):
    ack()
    respond("Generating *monthly summary* for your team...")
    run_pipeline(timeframe="monthly")
    _respond_with_report(respond)

def _respond_with_report(respond):
    try:
        with open("output/engineering_report.txt", "r", encoding="utf-8") as f:
            report = f.read()
        respond(f"*Engineering Report:*\n```{report[:2900]}```")
    except Exception as e:
        respond(f"❌ Error loading report: {e}")

def send_chart_to_slack(channel, file_path, title):
    try:
        with open(file_path, "rb") as f:
            response = app.client.files_upload_v2(
                channel=channel,
                file=f,
                title=title
            )
        return response
    except Exception as e:
        print(f"Error uploading file to Slack: {e}")


if __name__ == "__main__":
    print("🚀 Starting FIKA Slack Bot (Socket Mode)...")
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
