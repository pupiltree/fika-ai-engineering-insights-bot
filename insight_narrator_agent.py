from state_schema import MyState
import os
from dotenv import load_dotenv
load_dotenv()


def insight_narrator_agent(state: MyState) -> MyState:
    print("🧠 InsightNarratorAgent: generating summary...")
    churn = state["diff_summary"]["churn"]
    additions = state["diff_summary"]["additions"]
    state["insight"] = f"This week, total churn was {churn} lines of code. {additions} lines were added."
    return state

import requests

def send_to_slack(insight: str, author_stats: list):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    message = f"*Weekly Insight:*\n{insight}\n\n*Author Stats:*\n" + "\n".join(
        [f"- {a['author']}: ➕ {a['add']} | ➖ {a['del']} | 📁 {a['files']} files" for a in author_stats]
    )
    if not webhook_url:
        print("❌ Slack error: SLACK_WEBHOOK_URL is not set.")
        return
    response = requests.post(webhook_url, json={"text": message})
    if response.status_code != 200:
        print("❌ Slack error:", response.text)
    else:
        print("📤 Insight sent to Slack.")
