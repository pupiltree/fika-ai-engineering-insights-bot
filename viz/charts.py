import matplotlib.pyplot as plt

def plot_churn(churn_stats):
    authors = [c['author'] for c in churn_stats]
    churn = [c['churn'] for c in churn_stats]
    plt.bar(authors, churn)
    plt.title('Code Churn per Author')
    plt.savefig('churn.png')
