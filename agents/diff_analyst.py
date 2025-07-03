from langchain_core.runnables import Runnable
from collections import defaultdict

class DiffAnalystAgent(Runnable):
    """Processes GitHub event data to compute per-author churn stats."""

    def invoke(self, input, config=None):
        events = input.get("events", [])

        author_stats = defaultdict(lambda: {
            "additions": 0,
            "deletions": 0,
            "files_changed": 0,
            "churn": 0,
            "spike": False
        })

        for event in events:
            author = event["author"]
            additions = event["additions"]
            deletions = event["deletions"]
            files = event["files_changed"]
            churn = additions + deletions

            author_stats[author]["additions"] += additions
            author_stats[author]["deletions"] += deletions
            author_stats[author]["files_changed"] += files
            author_stats[author]["churn"] += churn

        for author, stats in author_stats.items():
            if stats["churn"] > 200:
                stats["spike"] = True

        return {"stats": dict(author_stats)}
