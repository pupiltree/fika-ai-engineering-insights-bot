import matplotlib.pyplot as plt
from collections import Counter
import os

def generate_commit_chart(metrics):
    authors = [item['author'] for item in metrics]
    churn_values = [item.get('churn', item.get('score', 0)) for item in metrics]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(authors, churn_values, color='skyblue')
    plt.title("Code Churn by Author")
    plt.xlabel("Author")
    plt.ylabel("Churn (Lines Changed)")
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, str(height), ha='center', va='bottom')

    chart_path = "data/commit_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def generate_commit_count_chart(metrics):
    authors = [item["author"] for item in metrics]
    commit_counts = Counter(authors)

    plt.figure(figsize=(6, 4))
    bars = plt.bar(commit_counts.keys(), commit_counts.values(), color='lightgreen')
    plt.title("Commits per Author")
    plt.xlabel("Author")
    plt.ylabel("Total Commits")
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, str(height), ha='center', va='bottom')

    chart_path = "data/commit_count_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

