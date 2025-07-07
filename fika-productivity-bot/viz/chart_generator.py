import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import os
from datetime import datetime


def generate_churn_chart(author_stats: dict, output_dir="viz", filename=None):
   
    if filename is None:
        filename = f"churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    authors = list(author_stats.keys())
    additions = [author_stats[a]["additions"] for a in authors]
    deletions = [author_stats[a]["deletions"] for a in authors]

    x = range(len(authors))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar(x, additions, width=width, label="Additions", color="green")
    plt.bar([i + width for i in x], deletions, width=width, label="Deletions", color="red")
    plt.xticks([i + width / 2 for i in x], authors, rotation=45, ha="right")
    plt.xlabel("Authors")
    plt.ylabel("Lines of Code")
    plt.title("Code Churn by Author")
    plt.legend()
    plt.tight_layout()

    plt.savefig(path)
    plt.close()
    return path
