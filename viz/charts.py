# import matplotlib.pyplot as plt

# def plot_churn(churn_stats):
#     authors = [c['author'] for c in churn_stats]
#     churn = [c['churn'] for c in churn_stats]
#     plt.bar(authors, churn)
#     plt.title('Code Churn per Author')
#     plt.savefig('churn.png')

import matplotlib.pyplot as plt
import os

def create_churn_chart(churn_data):
    """Create code churn visualization"""
    try:
        author_stats = churn_data.get('author_stats', {})
        
        if not author_stats:
            return None
        
        authors = list(author_stats.keys())
        churns = [stats['total_churn'] for stats in author_stats.values()]
        
        plt.figure(figsize=(10, 6))
        plt.bar(authors, churns, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.title('Code Churn by Author (Last Week)')
        plt.xlabel('Authors')
        plt.ylabel('Lines Changed')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = 'churn_chart.png'
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None
