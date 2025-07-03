from LangGraph.graph_builder import build_pipeline_graph, initialize_state
from insight_agents.narrator_agent import narrator_agent

if __name__ == "__main__":
    # Step 1: Build and run the graph
    graph = build_pipeline_graph()
    state = initialize_state({
        "repo_owner": "Dev-Rutwik",
        "repo_name": "Github_AI_Agent"
    })
    final_state = graph.invoke(state)
    print(final_state)
    analysis = final_state.get("developer_analysis", {})
    print(analysis)
    if not analysis:
        print("❌ Developer analysis not found in state.")
    else:
        print("✅ Developer Analysis Found.")
    
        # Step 3: Send to narrator agent for summarization
        summary = narrator_agent.invoke({"developer_analysis": analysis})

        print("\n GitHub Weekly Dev Report:\n")
        print(summary)
