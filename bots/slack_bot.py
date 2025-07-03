import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from agents.diff_analyst import analyze_churn
from agents.insight_narrator import generate_narrative
from bots.chart_generator import generate_commit_chart

# Load environment
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_CHANNEL_ID = "C0946MKJZSR"

def load_seed_data():
    with open("data/seed_data.json", "r") as f:
        return json.load(f)

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

@app.command("/dev-report")
def handle_dev_report(ack, respond, client):
    ack()

    try:
        # Step 1: Load and process data
        data = load_seed_data()
        churn_scores = analyze_churn(data)
        summary = generate_narrative(churn_scores)
        chart_path = generate_commit_chart(churn_scores)

        # Step 2: Upload image
        upload_response = client.files_upload_v2(
            file=chart_path,
            filename="churn_chart.png",
            title="Code Churn Chart",
            initial_comment="📊 *Weekly Dev Report:*",
            channels=[SLACK_CHANNEL_ID],
        )

        # Step 3: Post the summary as a separate message
        client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=f"*🧾 Summary Report:*\n{summary}"
        )

    except Exception as e:
        respond({
            "response_type": "ephemeral",
            "text": f"⚠️ Error: {str(e)}"
        })

if __name__ == "__main__":
    if not SLACK_APP_TOKEN:
        print("❌ Please set SLACK_APP_TOKEN in your .env file.")
    else:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
