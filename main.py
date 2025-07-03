from langgraph.graph import StateGraph, END
from agents.data_harvester import DataHarvesterAgent
from agents.diff_analyst import DiffAnalystAgent
from agents.insight_narrator import InsightNarratorAgent
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict, total=False):
    events: list
    stats: dict
    summary: str


# Define a shared state (dictionary)
class PipelineState(dict):
    pass

# Create the graph
graph = StateGraph(AgentState)

# Add nodes (agents)
graph.add_node("harvest", DataHarvesterAgent())
graph.add_node("analyze", DiffAnalystAgent())
graph.add_node("narrate", InsightNarratorAgent())

# Define flow: harvest → analyze → narrate → END
graph.set_entry_point("harvest")
graph.add_edge("harvest", "analyze")
graph.add_edge("analyze", "narrate")
graph.set_finish_point("narrate")

# Compile into an executable app
pipeline = graph.compile()

# Run it
if __name__ == "__main__":
    print("🔁 Running full LangGraph pipeline...\n")
    final_output = pipeline.invoke(PipelineState())
    print("📝 Final Summary:\n")
    print(final_output)
