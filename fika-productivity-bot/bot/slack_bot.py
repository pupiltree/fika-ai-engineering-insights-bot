# bot/slack_bot.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langgraph_app.graph_runner import run_productivity_report
from dotenv import load_dotenv
load_dotenv()  # Load .env file
from viz.chart_generator import generate_churn_chart

# Load from environment or hardcode during testing
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

# /dev-report slash command
@app.command("/dev-report")
def handle_dev_report(ack, body, client):
    ack()  # Always acknowledge the slash command

    try:
        # Step 1: Run LangGraph report
        report = run_productivity_report()
        report_data = report["data"]

        headline = report_data["headline"]
        insights = "\n• " + "\n• ".join(report_data["insights"])

        # Step 2: Generate chart image
        churn_chart_path = generate_churn_chart(report_data["author_stats"])

        # Step 3: Get the channel ID from body
        channel_id = body.get("channel_id")
        if not channel_id:
            raise ValueError("No channel_id found in request body.")

        # Step 4: Upload the file to the channel
        client.files_upload_v2(
            channel=channel_id,
            file=churn_chart_path,
            title="Code Churn by Author"
        )

        # Step 5: Send a message with the summary
        client.chat_postMessage(
            channel=channel_id,
            text=f"*{headline}*\n{insights}"
        )

    except Exception as e:
        # Post error message to channel
        client.chat_postMessage(
            channel=body.get("channel_id", ""),
            text=f":x: Error generating report:\n```{str(e)}```"
        )


# Run with socket mode (preferred for local + prod)
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
