from langgraph.graph import StateGraph
from agents.data_harvester import DataHarvesterAgent
from agents.diff_analyzer import DiffAnalyzerAgent
from agents.insight_narrator import InsightNarratorAgent

def get_insight_graph():
    builder = StateGraph()

    builder.add_node("harvester", DataHarvesterAgent())
    builder.add_node("analyzer", DiffAnalyzerAgent())
    builder.add_node("narrator", InsightNarratorAgent())

    builder.set_entry_point("harvester")
    builder.add_edge("harvester", "analyzer")
    builder.add_edge("analyzer", "narrator")

    return builder.compile()
