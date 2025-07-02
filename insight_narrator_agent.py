from state_schema import MyState

def insight_narrator_agent(state: MyState) -> MyState:
    print("🧠 InsightNarratorAgent: generating summary...")
    churn = state["diff_summary"]["churn"]
    additions = state["diff_summary"]["additions"]
    state["insight"] = f"This week, total churn was {churn} lines of code. {additions} lines were added."
    return state
