# main_graph.py
from langgraph.graph import StateGraph
from agents.data_harvester import data_harvester_node
from agents.diff_analyst import diff_analyst_node
from agents.insight_narrator import insight_narrator_node

# Declare the state as a dictionary
builder = StateGraph(dict)

builder.add_node("harvester", data_harvester_node)
builder.add_node("analyst", diff_analyst_node)
builder.add_node("narrator", insight_narrator_node)

builder.set_entry_point("harvester")
builder.add_edge("harvester", "analyst")
builder.add_edge("analyst", "narrator")

# Compile and run the graph
graph = builder.compile()

if __name__ == "__main__":
    print("🚀 Running LangGraph Dev Report...\n")
    result = graph.invoke({})
    print("\n✅ Final Summary:")
    print(result.get("summary", "No summary generated."))
