# =============================
# 🔧 Imports
# =============================
import streamlit as st
import matplotlib.pyplot as plt
import json

from langgraph.graph import StateGraph
from typing import TypedDict
import sqlite3
import datetime

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage


from dotenv import load_dotenv
import os

load_dotenv()  # 👈 loads from .env file
api_key = os.getenv("TOGETHER_API_KEY")

if not api_key:
    raise ValueError("Missing TOGETHER_API_KEY in environment")

os.environ["TOGETHER_API_KEY"] = api_key

# =============================
# 🔁 LangGraph Setup
# =============================
class DevState(TypedDict):
    data: dict


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

    prompt = f"""
You are an engineering analytics assistant.
Generate a concise, insightful summary of this week's performance from the following data:

✅ PRs merged: {weekly['pr_count']}
🕓 Lead time: {weekly['lead_time_days']} days
📈 Cycle time: {weekly['cycle_time_days']} days
❌ CI Failures: {weekly['ci_failures']}
🚀 Deploys: {weekly['deploys']}
🔁 Code churn: {churn}
⚠️ Risky days (high churn): {risks}
"""

    llm = ChatOpenAI(
        temperature=0,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Together-supported model
        base_url="https://api.together.xyz/v1",
        api_key=os.getenv("TOGETHER_API_KEY")
    )

    response = llm([HumanMessage(content=prompt)])

    return {
        "data": {
            "summary": response.content,
            "churn": churn
        }
    }



# LangGraph setup
workflow = StateGraph(DevState)
workflow.add_node("load", fetch_data)
workflow.add_node("analyze", analyze_data)
workflow.add_node("summarize", narrate_summary)
workflow.set_entry_point("load")
workflow.add_edge("load", "analyze")
workflow.add_edge("analyze", "summarize")
workflow.set_finish_point("summarize")
graph = workflow.compile()

# =============================
# 💻 Streamlit UI
# =============================
st.set_page_config(page_title="Dev Performance Bot", layout="centered")
st.title("📊 Dev Performance Bot (LangGraph MVP)")

st.markdown(
    "Click below to run the agent workflow and generate a dev report from seed GitHub data."
)

if st.button("▶️ Run /dev-report"):
    result = graph.invoke({"data": {}})
    today = datetime.date.today().isoformat()
    summary_text = result["data"]["summary"]
    churn = result["data"]["churn"]

    # Save to SQLite
    try:
        conn = sqlite3.connect("dev_reports.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                summary TEXT,
                churn TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO reports (date, summary, churn) VALUES (?, ?, ?)",
            (today, summary_text, json.dumps(churn)))
        conn.commit()
    except Exception as e:
        st.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

    # 🗂 View Past Reports from Dropdown
    conn = sqlite3.connect("dev_reports.db")
    cursor = conn.cursor()
    rows = cursor.execute("SELECT date, summary FROM reports ORDER BY id DESC").fetchall()
    conn.close()

    if rows:
        dates = [r[0] for r in rows]
        selected_date = st.selectbox("📅 View past report by date", dates)
        selected_summary = [r[1] for r in rows if r[0] == selected_date][0]

        if selected_date != today:
            st.markdown(f"**📆 {selected_date}**")
            st.info(selected_summary)



    # Show summary
    st.markdown("## 📝 Weekly Summary")
    st.success(summary_text)

    # Chart
    fig, ax = plt.subplots()
    ax.plot([f"Day {i+1}" for i in range(7)], churn, marker='o')
    ax.set_title("Code Churn Over 7 Days")
    ax.set_ylabel("Lines Changed")
    ax.set_xlabel("Day")
    st.pyplot(fig)

    st.caption(
        "Agent pipeline: DataHarvester → DiffAnalyst → InsightNarrator (via LangGraph)"
    )

    # Show past reports
    st.markdown("---")
    st.subheader("📅 Past Reports")
    conn = sqlite3.connect("dev_reports.db")
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT date, summary FROM reports ORDER BY id DESC LIMIT 5").fetchall(
        )
    conn.close()
    for date_str, past_summary in rows:
        st.markdown(f"**📆 {date_str}**")
        st.info(past_summary)

st.caption("LLM used: Together AI – Mixtral-8x7B-Instruct")
