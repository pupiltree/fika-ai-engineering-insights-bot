from collections import defaultdict
from state_schema import MyState

def author_stats_agent(state: MyState) -> MyState:
    print("🧑‍💻 AuthorStatsAgent: computing author-wise stats...")
    summary = defaultdict(lambda: {"add": 0, "del": 0, "files": 0})
    for e in state["events"]:
        summary[e["author"]]["add"] += e["add"]
        summary[e["author"]]["del"] += e["del"]
        summary[e["author"]]["files"] += e["files"]
    state["author_stats"] = [{"author": k, **v} for k, v in summary.items()]
    return state
