from state_schema import MyState

def diff_analyst_agent(state: MyState) -> MyState:
    print("📊 DiffAnalystAgent: analyzing diffs...")
    total_add = sum(e["add"] for e in state["events"])
    total_del = sum(e["del"] for e in state["events"])
    churn = total_add + total_del
    state["diff_summary"] = {
        "additions": total_add,
        "deletions": total_del,
        "churn": churn
    }
    return state
