import os
import requests
from dotenv import load_dotenv
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

# ---- Load GitHub Token ----
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ---- State Schema ----
class MyState(TypedDict):
    events: List[Dict]
    diff_summary: Dict
    insight: str


# ---- Helper: Fetch commit stats from PushEvents ----
def fetch_push_event_commits(owner, repo, token, per_page=5):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/events"
    response = requests.get(url, headers=headers, params={"per_page": per_page})

    results = []

    if response.status_code == 200:
        events = response.json()
        push_events = [e for e in events if e["type"] == "PushEvent"]

        for event in push_events:
            author = event["actor"]["login"]
            for commit in event["payload"]["commits"]:
                sha = commit["sha"]
                commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                commit_resp = requests.get(commit_url, headers=headers)

                if commit_resp.status_code == 200:
                    commit_data = commit_resp.json()
                    results.append({
                        "author": author,
                        "add": commit_data["stats"]["additions"],
                        "del": commit_data["stats"]["deletions"],
                        "files": commit_data["stats"]["total"]
                    })
                else:
                    print(f"⚠️ Failed to fetch commit {sha}")
    else:
        print("❌ GitHub API Error:", response.status_code, response.text)

    return results


# ---- Agent 1: Data Harvester ----
def data_harvester_agent(state: MyState) -> MyState:
    print("🛰️ DataHarvesterAgent: fetching real GitHub data...")
    
    owner = "vercel"
    repo = "next.js"

    real_events = fetch_push_event_commits(owner, repo, GITHUB_TOKEN, per_page=10)

    state["events"] = real_events
    return state



# ---- Agent 2: Diff Analyst ----
def diff_analyst_agent(state: MyState) -> MyState:
    print("📊 DiffAnalystAgent: analyzing diffs...")

    author_summary = {}
    total_add = 0
    total_del = 0

    for e in state["events"]:
        author = e["author"]
        add = e["add"]
        delete = e["del"]

        total_add += add
        total_del += delete

        if author not in author_summary:
            author_summary[author] = {"add": 0, "del": 0}
        
        author_summary[author]["add"] += add
        author_summary[author]["del"] += delete

    churn = total_add + total_del

    state["diff_summary"] = {
        "additions": total_add,
        "deletions": total_del,
        "churn": churn,
        "authors": author_summary
    }

    return state



# ---- Agent 3: Insight Narrator ----
def insight_narrator_agent(state: MyState) -> MyState:
    print("🧠 InsightNarratorAgent: generating summary...")

    churn = state["diff_summary"]["churn"]
    additions = state["diff_summary"]["additions"]
    authors = state["diff_summary"]["authors"]

    insight = f"This week, total churn was {churn} lines of code. {additions} lines were added.\n\n"

    insight += "📌 Author-wise Summary:\n"
    for author, stats in authors.items():
        insight += f"• {author}: +{stats['add']} / -{stats['del']}\n"

    state["insight"] = insight.strip()
    return state



# ---- Build LangGraph ----
builder = StateGraph(MyState)
builder.add_node("DataHarvester", RunnableLambda(data_harvester_agent))
builder.add_node("DiffAnalyst", RunnableLambda(diff_analyst_agent))
builder.add_node("InsightNarrator", RunnableLambda(insight_narrator_agent))

builder.set_entry_point("DataHarvester")
builder.add_edge("DataHarvester", "DiffAnalyst")
builder.add_edge("DiffAnalyst", "InsightNarrator")
builder.add_edge("InsightNarrator", END)

graph = builder.compile()

# ---- Run Graph ----
final_state = graph.invoke({
    "events": [],
    "diff_summary": {},
    "insight": ""
})

print("\n✅ Final Insight:", final_state["insight"])



#Testing purpose
