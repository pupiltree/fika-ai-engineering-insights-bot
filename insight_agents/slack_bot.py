# insight_agent/slack_bot.py

import os
from slack_bolt import App
from dotenv import load_dotenv
from insight_agents.narrator_agent import narrator_agent
from LangGraph.graph_builder import build_pipeline_graph, initialize_state

# Load .env variables
load_dotenv()

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
@app.command("/dev-report")
def handle_dev_report(ack, respond, command):
    ack()
    respond("⏳ Generating your GitHub report... Please wait.")
    user_question = command.get("text", "").strip().lower()

    graph = build_pipeline_graph()
    state = initialize_state({"repo_owner": "Dev-Rutwik", "repo_name": "Github_AI_Agent"})
    final_output = graph.invoke(state)

    developer_analysis = final_output["developer_analysis"]

    summary = narrator_agent.invoke({
        "developer_analysis": developer_analysis,
        "user_query": user_question
    })

    respond({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary
                }
            }
        ]
    })

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
