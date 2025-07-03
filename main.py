from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from state_schema import MyState
from fetch_github_events import data_harvester_agent
from diff_analyst_agent import diff_analyst_agent
from author_stats_agent import author_stats_agent
from insight_narrator_agent import insight_narrator_agent
import os
from insight_narrator_agent import send_to_slack 



builder = StateGraph(MyState)
builder.add_node("DataHarvester", RunnableLambda(data_harvester_agent))
builder.add_node("DiffAnalyst", RunnableLambda(diff_analyst_agent))
builder.add_node("AuthorStats", RunnableLambda(author_stats_agent))
builder.add_node("InsightNarrator", RunnableLambda(insight_narrator_agent))

builder.set_entry_point("DataHarvester")
builder.add_edge("DataHarvester", "DiffAnalyst")
builder.add_edge("DiffAnalyst", "AuthorStats")
builder.add_edge("AuthorStats", "InsightNarrator")
builder.add_edge("InsightNarrator", END)

graph = builder.compile()

final_state = graph.invoke({
    "events": [],
    "diff_summary": {},
    "insight": "",
    "author_stats": []
})

print("\n✅ Final Insight:", final_state["insight"])
print("👥 Author Stats:", final_state["author_stats"])

send_to_slack(final_state["insight"], final_state["author_stats"])

