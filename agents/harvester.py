import sqlite3

class DataHarvester:
    def __init__(self, db_path="fika_insights.db"):
        self.db_path = db_path

    def fetch_commits(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT author, date, additions, deletions, files_changed FROM commits")
        commits = cur.fetchall()
        conn.close()
        return commits

    def fetch_pull_requests(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT author, opened_at, closed_at, merged_at, additions, deletions, files_changed FROM pull_requests")
        prs = cur.fetchall()
        conn.close()
        return prs

if __name__ == "__main__":
    harvester = DataHarvester()
    commits = harvester.fetch_commits()
    prs = harvester.fetch_pull_requests()
    print(f"[✔] Loaded {len(commits)} commits and {len(prs)} pull requests from database.")
