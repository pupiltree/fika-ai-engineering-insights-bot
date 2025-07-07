# agents/diff_analyst.py

from typing import Dict, List
import pandas as pd


def analyze_diff(data: Dict[str, List[Dict]]) -> Dict:
    """Analyze churn from commit and PR data"""
    commits = pd.DataFrame(data.get("commits", []))
    prs = pd.DataFrame(data.get("prs", []))

    output = {}

    if not commits.empty:
        commits["timestamp"] = pd.to_datetime(commits["timestamp"])
        output["commit_churn_summary"] = _summarize_commit_churn(commits)
        output["churn_spikes"] = _detect_commit_spikes(commits)

        # ✅ Add author_stats extraction here
        author_stats = (
            commits.groupby("author")[["additions", "deletions"]]
            .sum()
            .astype(int)
            .to_dict(orient="index")
        )
        output["author_stats"] = author_stats

    if not prs.empty:
        prs["created_at"] = pd.to_datetime(prs["created_at"])
        prs["merged_at"] = pd.to_datetime(prs["merged_at"])
        output["pr_summary"] = _summarize_pr_stats(prs)

    return output



def _summarize_commit_churn(df: pd.DataFrame) -> Dict:
    """Aggregate churn per author and repo"""
    churn = df.groupby("author").agg({
        "additions": "sum",
        "deletions": "sum",
        "files_changed": "sum",
        "timestamp": "count"
    }).rename(columns={"timestamp": "commit_count"}).reset_index()

    return churn.to_dict(orient="records")


def _detect_commit_spikes(df: pd.DataFrame) -> List[Dict]:
    """Detect unusually large commits per author"""
    results = []
    avg_churn = df.groupby("author")[["additions", "deletions", "files_changed"]].mean().reset_index()
    for _, row in df.iterrows():
        author = row["author"]
        author_avg = avg_churn[avg_churn["author"] == author]
        if not author_avg.empty:
            avg = author_avg.iloc[0]
            if (
                row["additions"] > 2 * avg["additions"] or
                row["deletions"] > 2 * avg["deletions"] or
                row["files_changed"] > 2 * avg["files_changed"]
            ):
                results.append({
                    "author": author,
                    "timestamp": row["timestamp"],
                    "message": row["message"],
                    "additions": row["additions"],
                    "deletions": row["deletions"],
                    "files_changed": row["files_changed"],
                    "flag": "high churn"
                })
    return results


def _summarize_pr_stats(prs: pd.DataFrame) -> Dict:
    """Summarize PR lead time and size"""
    prs["lead_time_hours"] = (prs["merged_at"] - prs["created_at"]).dt.total_seconds() / 3600

    return {
        "avg_lead_time_hrs": round(prs["lead_time_hours"].mean(), 2),
        "avg_files_changed": round(prs["files_changed"].mean(), 1),
        "avg_additions": round(prs["additions"].mean(), 1),
        "avg_deletions": round(prs["deletions"].mean(), 1),
        "total_prs": len(prs)
    }


# For local test
if __name__ == "__main__":
    from data_harvester import harvest_data

    data = harvest_data()
    results = analyze_diff(data)
    print("Commit Summary:\n", results.get("commit_churn_summary"))
    print("\nChurn Spikes:\n", results.get("churn_spikes"))
    print("\nPR Summary:\n", results.get("pr_summary"))
