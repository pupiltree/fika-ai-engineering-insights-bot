from langchain_core.runnables import Runnable
from collections import defaultdict

class DiffAnalystAgent(Runnable):
    """Processes GitHub event data to compute per-author churn stats."""

    def invoke(self, events: list):
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

        # Flag churn spikes
        for author, stats in author_stats.items():
            if stats["churn"] > 200:
                stats["spike"] = True

        print("✅ DiffAnalystAgent: Computed stats for", len(author_stats), "authors.")
        return dict(author_stats)
