import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random

def generate_chart(output_path="output/dev_chart.png"):
    sns.set(style="whitegrid")

    contributors = ["alice", "bob", "carol", "jai.v"]
    commits = [random.randint(2, 7) for _ in contributors]
    additions = [random.randint(50, 250) for _ in contributors]

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    # Bar chart: commits
    sns.barplot(x=contributors, y=commits, ax=axs[0], palette="Blues_d")
    axs[0].set_title("Commits per Contributor")
    axs[0].set_ylabel("Commits")

    # Line plot: additions
    sns.lineplot(x=contributors, y=additions, ax=axs[1], marker='o', color="orange")
    axs[1].set_title("Lines Added")
    axs[1].set_ylabel("Lines")

    plt.tight_layout()
    os.makedirs("output", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
