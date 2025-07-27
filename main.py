import os
import json
from dotenv import load_dotenv
from agents.data_harvester import DataHarvester
from agents.diff_analyst import DiffAnalyst
from agents.insight_narrator import InsightNarrator
from storage.database import Database
from slack_bot.bot import app
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()

class State(TypedDict):
    data: dict
    metrics: dict
    report: str

def load_seed_data():
    print("📦 Loading seed data...")
    harvester = DataHarvester("dummy_token", "dummy/repo")

    # ✅ Check if database already has data
    db = Database()
    if db.get_commits() or db.get_prs():
        print("✅ Data already exists in database. Skipping seeding.")
        return

    # ✅ If empty, load seed_data.json if it exists
    if os.path.exists("data/seed_data.json"):
        with open("data/seed_data.json") as f:
            data = json.load(f)
            for item in data:
                if "sha" in item:
                    harvester.db.store_commit(item)
                elif "number" in item:
                    harvester.db.store_pr(item)
        print("🌱 Loaded data from seed_data.json")

    # ✅ Then insert dummy commits and PRs
    try:
        from seed_dummy_commits import insert_dummy_commits
        from seed_dummy_prs import insert_dummy_prs

        insert_dummy_commits()
        insert_dummy_prs()
        print("🌱 Dummy commits and PRs inserted successfully!")
    except Exception as e:
        print("⚠️ Error inserting dummy seed data:", e)

def run_harvester(state: State) -> State:
    harvester = DataHarvester("dummy_token", "dummy/repo")
    state["data"] = {
        "commits": harvester.db.get_commits(),
        "prs": harvester.db.get_prs()
    }
    return state

def run_analyst(state: State) -> State:
    analyst = DiffAnalyst()
    state["metrics"] = analyst.analyze()
    return state

def run_narrator(state: State) -> State:
    narrator = InsightNarrator()
    state["report"] = narrator.generate_report(period="weekly")  # ✅ FIXED HERE
    return state

# LangGraph workflow setup
workflow = StateGraph(State)
workflow.add_node("harvester", run_harvester)
workflow.add_node("analyst", run_analyst)
workflow.add_node("narrator", run_narrator)
workflow.add_edge("harvester", "analyst")
workflow.add_edge("analyst", "narrator")
workflow.add_edge("narrator", END)
workflow.set_entry_point("harvester")
graph = workflow.compile()

def main():
    load_seed_data()
    print("⚙️ Running agent pipeline...")
    result = graph.invoke({"data": {}, "metrics": {}, "report": ""})
    print("📝 Final Report:\n", result["report"])

    print("🤖 Starting Slack bot using Socket Mode...")
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == "__main__":
    main()
