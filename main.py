print("🔍 main.py reached")

from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from src.bots.slack_bot import app
from src.agents.data_harvester import data_harvester_node
from src.agents.diff_analyst import diff_analyst_node
from src.agents.forecaster import forecast_node
from src.agents.influence_map import influence_map_node
from src.agents.insight_narrator import insight_narrator_node

# Define what data flows through the graph
class DevState(TypedDict):
    commits: List[dict]
    churn: int
    forecast_churn: int
    influence_map: Dict[str, List[str]]
    summary: str

def build_graph():
    builder = StateGraph(DevState)

    builder.add_node("harvest", data_harvester_node)
    builder.add_node("analyze", diff_analyst_node)
    builder.add_node("forecast", forecast_node)
    builder.add_node("influence_map", influence_map_node)
    builder.add_node("narrate", insight_narrator_node)

    builder.set_entry_point("harvest")
    builder.add_edge("harvest", "analyze")
    builder.add_edge("analyze", "forecast")
    builder.add_edge("forecast", "influence_map")
    builder.add_edge("influence_map", "narrate")

    return builder.compile()

print("🔍 main.py reached again")

if __name__ == "__main__":
    graph = build_graph()
    graph.invoke({})
    print("🚀 Starting Slack bot on port 3047...")
    app.start(port=3047)
