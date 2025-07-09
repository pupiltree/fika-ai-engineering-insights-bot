# =============================
# 🔧 Imports
# =============================
import streamlit as st
import matplotlib.pyplot as plt
import json

from langgraph.graph import StateGraph
from langgraph.schema import StateSchema
from typing import TypedDict

# =============================
# 🔁 LangGraph Setup
# =============================

class DevState(TypedDict):
    data: dict

# Pure functions that work with LangGraph
def fetch_data(state: DevState) -> DevState:
    with open("seed_data.json") as f:
        return {"data": json.load(f)}

def analyze_data(state: DevState) -> DevState:
    data = state["data"]
    churn = data["diff_churn"]
    risks = [i for i, c in enumerate(churn) if c > 200]
    return {
        "data": {
            "churn": churn,
            "risks": risks,
            "weekly": data["weekly_stats"]
        }
    }

def narrate_summary(state: DevState) -> DevState:
    d = state["data"]
    churn = d["churn"]
    risks = d["risks"]
    weekly = d["weekly"]
    summary = (
        f"✅ {weekly['pr_count']} PRs merged\n"
        f"🕓 Lead Time: {weekly['lead_time_days']} days\n"
        f"📈 Cycle Time: {weekly['cycle_time_days']} days\n"
        f"❌ CI Failures: {weekly['ci_failures']}\n"
        f"🚀 Deploys: {weekly['deploys']}\n"
    )
    if risks:
        summary += f"\n⚠️ Risky churn on days: {', '.join(['Day '+str(r+1) for r in risks])}"
    return {"data": {"summary": summary, "churn": churn}}

# Define workflow
workflow = StateGraph(DevState)
workflow.add_node("load", fetch_data)
workflow.add_node("analyze", analyze_data)
workflow.add_node("summarize", narrate_summary)

workflow.set_entry_point("load")
workflow.add_edge("load", "analyze")
workflow.add_edge("analyze", "summarize")
workflow.set_finish_point("summarize")

graph = workflow.compile(state_schema=StateSchema(DevState))

# =============================
# 💻 Streamlit UI
# =============================

st.set_page_config(page_title="Dev Performance Bot", layout="centered")
st.title("📊 Dev Performance Bot (LangGraph MVP)")

st.markdown("Click below to run the agent workflow and generate a dev report from seed GitHub data.")

if st.button("▶️ Run /dev-report"):
    result = graph.invoke({"data": {}})

    st.markdown("## 📝 Weekly Summary")
    st.success(result["data"]["summary"])

    churn = result["data"]["churn"]
    fig, ax = plt.subplots()
    ax.plot([f"Day {i+1}" for i in range(7)], churn, marker='o')
    ax.set_title("Code Churn Over 7 Days")
    ax.set_ylabel("Lines Changed")
    ax.set_xlabel("Day")
    st.pyplot(fig)

    st.caption("Agent pipeline: DataHarvester → DiffAnalyst → InsightNarrator (via LangGraph)")
