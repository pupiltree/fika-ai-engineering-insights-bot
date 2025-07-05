# influence_map.py
# Code review influence map graph generation
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime, timedelta
import io
import logging

def extract_review_data(pr_data: List) -> List[Dict]:
    """Extract review relationships from PR data."""
    review_relationships = []
    
    for pr in pr_data:
        if 'reviews' in pr and pr['reviews']:
            author = pr.get('user', {}).get('login', 'Unknown')
            pr_size = pr.get('additions', 0) + pr.get('deletions', 0)
            
            for review in pr['reviews']:
                reviewer = review.get('user', {}).get('login', 'Unknown')
                state = review.get('state', 'COMMENTED')  # APPROVED, CHANGES_REQUESTED, COMMENTED
                submitted_at = review.get('submitted_at')
                
                # Calculate review impact score
                impact_score = calculate_review_impact(state, pr_size)
                
                review_relationships.append({
                    'author': author,
                    'reviewer': reviewer,
                    'state': state,
                    'impact_score': impact_score,
                    'pr_size': pr_size,
                    'submitted_at': submitted_at
                })
    
    return review_relationships

def calculate_review_impact(state: str, pr_size: int) -> float:
    """Calculate the impact score of a review."""
    base_scores = {
        'APPROVED': 1.0,
        'CHANGES_REQUESTED': 0.5,  # Lower score for blocking reviews
        'COMMENTED': 0.8,
        'DISMISSED': 0.0
    }
    
    base_score = base_scores.get(state, 0.5)
    
    # Adjust for PR size (larger PRs have more impact)
    size_factor = min(pr_size / 100, 2.0)  # Cap at 2x for very large PRs
    
    return base_score * size_factor

def build_influence_graph(review_data: List[Dict]) -> nx.DiGraph:
    """Build a directed graph of review relationships."""
    G = nx.DiGraph()
    
    # Add nodes and edges
    for review in review_data:
        author = review['author']
        reviewer = review['reviewer']
        impact = review['impact_score']
        
        # Add nodes if they don't exist
        if not G.has_node(author):
            G.add_node(author, type='author', total_reviews=0, total_impact=0)
        if not G.has_node(reviewer):
            G.add_node(reviewer, type='reviewer', total_reviews=0, total_impact=0)
        
        # Add or update edge
        if G.has_edge(reviewer, author):
            # Update existing edge
            current_weight = G[reviewer][author]['weight']
            current_count = G[reviewer][author]['count']
            G[reviewer][author]['weight'] = (current_weight + impact) / 2
            G[reviewer][author]['count'] = current_count + 1
        else:
            # Add new edge
            G.add_edge(reviewer, author, weight=impact, count=1)
        
        # Update node attributes
        G.nodes[reviewer]['total_reviews'] += 1
        G.nodes[reviewer]['total_impact'] += impact
        G.nodes[author]['total_impact'] += impact
    
    return G

def calculate_influence_metrics(G: nx.DiGraph) -> Dict:
    """Calculate influence metrics for each node."""
    metrics = {}
    
    for node in G.nodes():
        # In-degree (how many people review this person's code)
        in_degree = G.in_degree(node)
        
        # Out-degree (how many people this person reviews)
        out_degree = G.out_degree(node)
        
        # PageRank (overall influence in the network)
        try:
            pagerank = nx.pagerank(G, weight='weight')[node]
        except:
            pagerank = 0.0
        
        # Average impact of reviews given
        if out_degree > 0:
            avg_impact = G.nodes[node]['total_impact'] / G.nodes[node]['total_reviews']
        else:
            avg_impact = 0.0
        
        # Betweenness centrality (how central this person is in the review network)
        try:
            betweenness = nx.betweenness_centrality(G, weight='weight')[node]
        except:
            betweenness = 0.0
        
        metrics[node] = {
            'in_degree': in_degree,
            'out_degree': out_degree,
            'pagerank': pagerank,
            'avg_impact': avg_impact,
            'betweenness': betweenness,
            'total_reviews': G.nodes[node]['total_reviews'],
            'total_impact': G.nodes[node]['total_impact']
        }
    
    return metrics

def generate_influence_map_chart(G: nx.DiGraph, metrics: Dict) -> io.BytesIO:
    """Generate a visual influence map chart."""
    plt.figure(figsize=(12, 10))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Node sizes based on total impact
    node_sizes = [metrics[node]['total_impact'] * 100 for node in G.nodes()]
    
    # Node colors based on role (author vs reviewer)
    node_colors = []
    for node in G.nodes():
        if G.nodes[node]['total_reviews'] > 0:
            node_colors.append('lightblue')  # Active reviewer
        else:
            node_colors.append('lightcoral')  # Author only
    
    # Edge weights for thickness
    edge_weights = [G[u][v]['weight'] * 3 for u, v in G.edges()]
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6, edge_color='gray', arrows=True, arrowsize=20)
    
    # Add labels with influence scores
    labels = {}
    for node in G.nodes():
        pagerank = metrics[node]['pagerank']
        labels[node] = f"{node}\n({pagerank:.2f})"
    
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='lightblue', label='Active Reviewer'),
        mpatches.Patch(color='lightcoral', label='Author Only')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.title('Code Review Influence Map\n(Node size = Total Impact, Edge thickness = Review Weight)', 
              fontsize=14, fontweight='bold')
    plt.axis('off')
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

def generate_influence_summary(metrics: Dict) -> str:
    """Generate a human-readable summary of influence metrics."""
    lines = []
    lines.append("**🔍 Code Review Influence Analysis:**")
    
    # Find top influencers
    influencers = sorted(metrics.items(), key=lambda x: x[1]['pagerank'], reverse=True)[:5]
    lines.append("\n**Top Influencers (PageRank):**")
    for i, (name, metric) in enumerate(influencers, 1):
        lines.append(f"{i}. **{name}**: {metric['pagerank']:.3f} (reviews: {metric['total_reviews']})")
    
    # Find most active reviewers
    reviewers = [(name, metric) for name, metric in metrics.items() if metric['total_reviews'] > 0]
    top_reviewers = sorted(reviewers, key=lambda x: x[1]['total_reviews'], reverse=True)[:5]
    
    lines.append("\n**Most Active Reviewers:**")
    for i, (name, metric) in enumerate(top_reviewers, 1):
        avg_impact = metric['avg_impact']
        impact_emoji = "🟢" if avg_impact > 1.0 else "🟡" if avg_impact > 0.5 else "🔴"
        lines.append(f"{i}. **{name}**: {metric['total_reviews']} reviews ({impact_emoji} avg impact: {avg_impact:.2f})")
    
    # Find review bottlenecks (people who get reviewed a lot but don't review others)
    bottlenecks = [(name, metric) for name, metric in metrics.items() 
                   if metric['in_degree'] > 2 and metric['out_degree'] < 2]
    if bottlenecks:
        lines.append("\n**⚠️ Potential Review Bottlenecks:**")
        for name, metric in bottlenecks:
            lines.append(f"• **{name}**: {metric['in_degree']} incoming reviews, {metric['out_degree']} outgoing")
    
    # Network health metrics
    total_nodes = len(metrics)
    active_reviewers = len([m for m in metrics.values() if m['total_reviews'] > 0])
    review_coverage = (active_reviewers / total_nodes * 100) if total_nodes > 0 else 0
    
    lines.append(f"\n**Network Health:**")
    lines.append(f"• Total contributors: {total_nodes}")
    lines.append(f"• Active reviewers: {active_reviewers} ({review_coverage:.1f}%)")
    
    if review_coverage < 50:
        lines.append("⚠️ **Warning**: Low review participation - consider encouraging more team members to review")
    
    return '\n'.join(lines)

def create_influence_map(pr_data: List) -> Tuple[io.BytesIO, str]:
    """Main function to create influence map from PR data."""
    try:
        # Extract review relationships
        review_data = extract_review_data(pr_data)
        
        if not review_data:
            return None, "No review data available for influence map generation."
        
        # Build influence graph
        G = build_influence_graph(review_data)
        
        if len(G.nodes()) < 2:
            return None, "Insufficient review relationships for influence map."
        
        # Calculate metrics
        metrics = calculate_influence_metrics(G)
        
        # Generate chart
        chart_buf = generate_influence_map_chart(G, metrics)
        
        # Generate summary
        summary = generate_influence_summary(metrics)
        
        return chart_buf, summary
        
    except Exception as e:
        logging.error(f"Error creating influence map: {e}")
        return None, f"Error generating influence map: {str(e)}" 