from langgraph.graph import StateGraph, END
from data_Harvester.data_harvester_agent import data_harvester_agent
from typing import TypedDict, List,Dict
from data_analyst_agent.diff_agent import diff_analyst_agent
from insight_agents.narrator_agent import narrator_agent
# ✅ 1. Define the shape of your state
class AgentState(TypedDict):
    repo_owner: str
    repo_name: str
    commits: List[dict]
    pull_requests: List[dict]
    developer_analysis: Dict  # ✅ Add this line
    narration: str
# ✅ 2. Entry-point state init
def initialize_state(input_data: dict) -> AgentState:
    return {
        "repo_owner": input_data["repo_owner"],
        "repo_name": input_data["repo_name"],
        "commits": [],
        "pull_requests": []
    }

#   3. Agent who will get Raw Data
def run_data_harvester(state: AgentState) -> AgentState:
    response = data_harvester_agent.invoke({
        "repo_owner": state["repo_owner"],
        "repo_name": state["repo_name"]
    })
    state["commits"] = response["commits"]
    state["pull_requests"] = response["pull_requests"]
    return state

#   4. Agent who will preprocess the Data
def run_diff_analyst(state: AgentState) -> AgentState:
    result = diff_analyst_agent.invoke({
        "commits": state["commits"],
        "pull_requests": state["pull_requests"]
    })
    state["developer_analysis"] = result
    state["pull_requests"] = []
    state["commits"] = []
    return state

def run_narrator(state: AgentState) -> AgentState:
    summary = narrator_agent.invoke({"developer_analysis": state["developer_analysis"]})
    state["narration"] = summary
    return state

# ✅ 5. Graph builder
def build_pipeline_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("harvest", run_data_harvester)
    workflow.add_node("diff_analyst", run_diff_analyst)
    workflow.add_node("narrator", run_narrator)  

    workflow.set_entry_point("harvest")
    workflow.add_edge("harvest", "diff_analyst")
    workflow.add_edge("diff_analyst", "narrator") 
    workflow.set_finish_point("narrator") 

    return workflow.compile()

