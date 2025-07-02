from collections import defaultdict

def diff_analyst_node(state):  
    print("\n📊 [DiffAnalystAgent] Analyzing commit data...")
    
    data = state.get("commits", []) 
    
    
    churn_by_user = defaultdict(lambda: {"commits": 0, "lines_added": 0, "lines_deleted": 0})

    for entry in data:
        user = entry["author"]
        churn_by_user[user]["commits"] += 1
        churn_by_user[user]["lines_added"] += entry["additions"]
        churn_by_user[user]["lines_deleted"] += entry["deletions"]

    
    enhanced_analysis = defaultdict(lambda: {
        "commits": 0, 
        "lines_added": 0, 
        "lines_deleted": 0,
        "large_commits": 0,
        "late_commits": 0,
        "commit_types": defaultdict(int),
        "files_touched": set(),
        "avg_commit_size": 0,
        "churn_ratio": 0,
        "most_active_hour": 12,
        "most_active_day": "Unknown"
    })

    
    time_patterns = {
        "hourly_distribution": defaultdict(int),
        "daily_distribution": defaultdict(int)
    }

    for entry in data:
        user = entry["author"]
        
        
        enhanced_analysis[user]["commits"] += 1
        enhanced_analysis[user]["lines_added"] += entry["additions"]
        enhanced_analysis[user]["lines_deleted"] += entry["deletions"]
        
        
        if entry.get("is_large_commit", False):
            enhanced_analysis[user]["large_commits"] += 1
            
        if entry.get("is_late_commit", False):
            enhanced_analysis[user]["late_commits"] += 1
            
        commit_type = entry.get("commit_type", "other")
        enhanced_analysis[user]["commit_types"][commit_type] += 1
        
        
        for file_change in entry.get("files_changed", []):
            enhanced_analysis[user]["files_touched"].add(file_change["filename"])
        
        
        hour = entry.get("hour", 12)
        day = entry.get("day_of_week", "Unknown")
        time_patterns["hourly_distribution"][hour] += 1
        time_patterns["daily_distribution"][day] += 1

    
    for user, stats in enhanced_analysis.items():
        if stats["commits"] > 0:
            stats["avg_commit_size"] = (stats["lines_added"] + stats["lines_deleted"]) / stats["commits"]
            stats["churn_ratio"] = stats["lines_deleted"] / max(stats["lines_added"], 1)
            stats["files_touched"] = len(stats["files_touched"])

    
    for user, stats in churn_by_user.items():
        print(f"→ {user}: {stats}")

    print("✅ Analysis complete.")
    
    
    state["analysis"] = churn_by_user
    
    
    state["enhanced_analysis"] = dict(enhanced_analysis)
    state["time_patterns"] = {
        "hourly": dict(time_patterns["hourly_distribution"]),
        "daily": dict(time_patterns["daily_distribution"])
    }
    
    return state