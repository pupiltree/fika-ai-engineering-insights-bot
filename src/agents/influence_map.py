from langchain_core.runnables import Runnable

@Runnable
def influence_map_node(state):
    prs = state.get("commits", [])
    influence_map = {}
    for pr in prs:
        author = pr.get("author")
        reviewers = pr.get("reviewers", [])
        for reviewer in reviewers:
            influence_map.setdefault(reviewer, set()).add(author)

    result = {k: list(v) for k, v in influence_map.items()}
    state["influence_map"] = result
    return state
