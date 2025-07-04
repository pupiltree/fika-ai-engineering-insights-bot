from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
import json

from agents.diff_analyst import analyze_churn
from agents.insight_narrator import generate_narrative

# ✅ Define the shared state format
class AgentState(TypedDict):
    raw_data: list
    churn_data: list
    narrative: str

# ✅ Agent 1: Harvester
def data_harvester_agent(state: AgentState) -> AgentState:
    print("🔁 Data Harvester Running")
    with open("data/seed_data.json", "r") as f:
        raw_data = json.load(f)
    state["raw_data"] = raw_data
    return state

# ✅ Agent 2: Diff Analyst
def diff_analyst_agent(state: AgentState) -> AgentState:
    print("📊 Diff Analyst Running")
    churn_data = analyze_churn(state.get("raw_data", []))
    state["churn_data"] = churn_data
    return state

# ✅ Agent 3: Insight Narrator
def insight_narrator_agent(state: AgentState) -> AgentState:
    print("🧠 Insight Narrator Running")
    summary = generate_narrative(state.get("churn_data", []))
    state["narrative"] = summary
    return state

# ✅ Build LangGraph with schema
builder = StateGraph(AgentState)
builder.add_node("Harvester", RunnableLambda(data_harvester_agent))
builder.add_node("Analyst", RunnableLambda(diff_analyst_agent))
builder.add_node("Narrator", RunnableLambda(insight_narrator_agent))

builder.set_entry_point("Harvester")
builder.add_edge("Harvester", "Analyst")
builder.add_edge("Analyst", "Narrator")

graph = builder.compile()

# ✅ Run the graph
if __name__ == "__main__":
    result = graph.invoke({})
    print("\n✅ Final Narrative:\n", result["narrative"])
