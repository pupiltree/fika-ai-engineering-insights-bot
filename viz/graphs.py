import matplotlib.pyplot as plt
import networkx as nx
import os
import json
from storage.database import Database

def generate_review_influence_map():
    db = Database()
    prs = db.get_prs(30)  # Get PRs from the last 30 days
    G = nx.DiGraph()

    for pr in prs:
        author = getattr(pr, "author", None)
        raw_reviewers = getattr(pr, "reviewers", "[]")
        try:
            reviewers = json.loads(raw_reviewers)
        except (json.JSONDecodeError, TypeError):
            reviewers = []

        # Only continue if both author and reviewers are present
        if not author or not reviewers:
            continue

        for reviewer in reviewers:
            if reviewer != author:
                G.add_edge(reviewer, author)  # Reviewer influences author

    # Don't plot if graph is empty
    if G.number_of_edges() == 0:
        print("❌ No review relationships found to plot.")
        return None

    # Draw the graph
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # consistent layout
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1500, alpha=0.9)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title("🔄 Code Review Influence Map")
    plt.axis("off")

    # Save the plot
    output_path = "viz/review_map.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"✅ Influence graph saved to {output_path}")
    return output_path

# Optional: Run directly
if __name__ == "__main__":
    generate_review_influence_map()
