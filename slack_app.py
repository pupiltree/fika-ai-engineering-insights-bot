import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from generate_fake_chart import generate_chart
from slack_sdk import WebClient
from graph.pipeline import build_graph

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.command("/dev-report")
def handle_dev_report(ack, body, respond, client: WebClient):
    print("🔧 /dev-report command triggered")
    ack()

    # Step 1: Run LangGraph pipeline
    workflow = build_graph()
    state = {
        "repo": "pupiltree/fika-ai-engineering-insights-bot",
        "time_window": "weekly"
    }
    result = workflow.invoke(state)

    # Step 2: Generate chart
    image_path = "output/dev_chart.png"
    generate_chart(image_path)

    # Step 3: Upload chart to Slack
    with open(image_path, "rb") as file_content:
        client.files_upload_v2(
            channel=body["channel_id"],
            file=file_content,
            filename="dev_report_chart.png",
            title="Weekly Dev Report"
        )

    # Step 4: Send AI-generated insight summary
    summary = result.get("insight_summary", "⚠️ No summary generated.")
    respond(f"📡 *Weekly Summary:*\n{summary}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
