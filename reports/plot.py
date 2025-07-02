import matplotlib.pyplot as plt
import os

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

def plot_commits_vs_prs(commits_count, prs_count):
    plt.figure(figsize=(6, 4))
    bars = plt.bar(["Commits", "PRs"], [commits_count, prs_count], color=["skyblue", "lightgreen"])
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.0f}", ha='center')
    plt.title("Commits vs PRs")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("reports/commits_vs_prs.png")
    plt.close()
    print("[✔] Generated reports/commits_vs_prs.png")

def plot_churn_per_author(author_churns):
    if not author_churns:
        print("[⚠️] No author churn data to plot.")
        return
    authors, churns = zip(*author_churns)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(authors, churns, color="orange")
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 10, f"{int(yval)}", ha='center')
    plt.title("Churn Per Author")
    plt.xlabel("Author")
    plt.ylabel("Total Churn (lines)")
    plt.tight_layout()
    plt.savefig("reports/churn_per_author.png")
    plt.close()
    print("[✔] Generated reports/churn_per_author.png")
