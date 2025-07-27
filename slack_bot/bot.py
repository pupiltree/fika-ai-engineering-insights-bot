from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agents.insight_narrator import InsightNarrator
from viz.charts import generate_churn_chart
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack App
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

def send_report(period, say, with_chart=False, channel_id=None):
    try:
        narrator = InsightNarrator()
        report_text, _ = narrator.generate_report(period=period)
        say(text=report_text)

        if with_chart and period == "weekly":
            chart_path = generate_churn_chart()

            if os.path.exists(chart_path):
                # 🔧 TEMP FIX for deprecated files.upload
                say(
                    text=f"🖼️ Weekly Churn Chart generated and saved locally at:\n`{chart_path}`\nYou can open or upload it manually to Slack."
                )

                # 🔧 Optional Future: Use chat_postMessage + image block if image is hosted externally
                # app.client.chat_postMessage(
                #     channel=channel_id,
                #     blocks=[
                #         {
                #             "type": "image",
                #             "image_url": "https://your-cdn-or-s3-link/chart.png",
                #             "alt_text": "Weekly Churn Chart"
                #         }
                #     ]
                # )
    except Exception as e:
        say(f"❌ Failed to generate {period} report: {str(e)}")

# ✅ Slash command for weekly report
@app.command("/weekly-report")
def weekly_report(ack, say, body):
    ack()
    channel_id = body.get("channel_id")
    send_report("weekly", say, with_chart=True, channel_id=channel_id)

# ✅ Slash command for daily report
@app.command("/daily-report")
def daily_report(ack, say, body):
    ack()
    channel_id = body.get("channel_id")
    send_report("daily", say, channel_id=channel_id)

# ✅ Slash command for monthly report
@app.command("/monthly-report")
def monthly_report(ack, say, body):
    ack()
    channel_id = body.get("channel_id")
    send_report("monthly", say, channel_id=channel_id)

# ✅ Start SocketMode handler
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
