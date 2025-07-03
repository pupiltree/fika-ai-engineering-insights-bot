
from typing import List
from dateutil.parser import parse
def data_analytics(commits: List[dict], pull_request: List[dict]) -> dict:
    
    total_commits = len(commits)
    total_pull_requests = len(pull_request)   
    developer_analysis = {"total_commits": 0, "total_pull_requests": 0, "developer_summary" : {}, "risky_files":[],"churn_summary":{},"commit_message_tags": {"fix": 0, "refactor": 0, "feat": 0}
}
    developer_analysis["total_commits"] = total_commits
    developer_analysis["total_pull_requests"] = total_pull_requests
    
    for commit in commits:
        author = commit["author"]
        dt = parse(commit["date"])
        formatted_date = dt.strftime("%B-%d-%Y")

        if author not in developer_analysis["developer_summary"]:
            developer_analysis["developer_summary"][author] = {"commits": 0,"additions": 0, "deletion": 0, "changes": 0,"timestamps": [],"dates_committed":[] }
        developer_analysis["developer_summary"][author]["commits"] += 1
        developer_analysis["developer_summary"][author]["timestamps"].append(dt)
        if formatted_date not in developer_analysis["developer_summary"][author]["dates_committed"]:
            developer_analysis["developer_summary"][author]["dates_committed"].append(formatted_date)
        msg = commit["message"].lower()
        if "fix" in msg: developer_analysis["commit_message_tags"]["fix"] += 1
        if "refactor" in msg: developer_analysis["commit_message_tags"]["refactor"] += 1
        if "feat" in msg or "feature" in msg: developer_analysis["commit_message_tags"]["feat"] += 1
        
    for author, data in developer_analysis["developer_summary"].items():
        timestamps = sorted(data["timestamps"])
        deltas = []
        
        if len(timestamps) >= 2:
            for i in range(1, len(timestamps)):
                delta = timestamps[i] - timestamps[i-1]
                deltas.append(delta)
            
            avg_seconds = sum(d.total_seconds() for d in deltas) / len(deltas)
            data["avg_commit_interval_hours"] = avg_seconds / 3600
            data["commit_frequency"] = f"Every {avg_seconds/3600:.1f} hours"
        else:
            data["avg_commit_interval_hours"] = None
            data["commit_frequency"] = "Insufficient data"
    
        data["timestamps"] = []
    
    for pr in pull_request:
        author = pr["user"]
        if author not in developer_analysis["developer_summary"]:
            developer_analysis["developer_summary"][author] = {"commits": 0,"additions": 0, "deletion": 0, "changes": 0,"timestamps": []}
        developer_analysis["developer_summary"][author]["additions"] += pr["additions"]
        developer_analysis["developer_summary"][author]["deletion"] += pr["deletions"]
        developer_analysis["developer_summary"][author]["changes"] += pr["changes"]
        if pr["changes"]>100:
            risk_analysis = {}
            risk_analysis = {"file name":"","changes":0,"status":""}
            risk_analysis["file name"] = pr["filename"]
            risk_analysis["changes"] = pr["changes"]
            risk_analysis["status"] = pr["status"]
            developer_analysis["risky_files"].append(risk_analysis)

    developer_analysis["churn_summary"] = {
    "total_additions": sum(dev["additions"] for dev in developer_analysis["developer_summary"].values()),
    "total_deletions": sum(dev["deletion"] for dev in developer_analysis["developer_summary"].values()),
    "total_changes": sum(dev["changes"] for dev in developer_analysis["developer_summary"].values())
}
    return developer_analysis