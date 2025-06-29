def analyze_diff(commits):
    churn_stats = []
    for c in commits:
        churn = c['additions'] + c['deletions']
        churn_stats.append({
            'author': c['author'],
            'churn': churn,
            'files_changed': c['changed_files'],
            'commit_id': c['sha']
        })
    # Flag spikes/outliers
    return churn_stats
