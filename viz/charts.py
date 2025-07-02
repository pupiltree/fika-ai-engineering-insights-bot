import matplotlib.pyplot as plt
from storage.database import Database
import os

def generate_churn_chart(days=7):
    db = Database()
    commits = db.get_commits(days)

    if not commits:
        return None  # no data to plot

    author_churn = {}
    for c in commits:
        author_churn[c.author] = author_churn.get(c.author, 0) + (c.additions + c.deletions)

    authors = list(author_churn.keys())
    churns = list(author_churn.values())

    plt.figure(figsize=(10, 6))
    plt.bar(authors, churns, color='skyblue')
    plt.xlabel("Authors")
    plt.ylabel("Churn (Lines Added + Deleted)")
    plt.title("Weekly Code Churn by Author")
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_path = "data/churn_chart.png"
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path)
    plt.close()

    return os.path.abspath(chart_path)
