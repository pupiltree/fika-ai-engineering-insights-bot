import requests
from datetime import datetime, timedelta
from storage.database import Database

class DataHarvester:
    def __init__(self, github_token, repo):
        self.github_token = github_token
        self.repo = repo
        self.db = Database()
        self.headers = {"Authorization": f"token {github_token}"}

    def fetch_prs(self):
        url = f"https://api.github.com/repos/{self.repo}/pulls?state=all"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        prs = response.json()

        for pr in prs:
            pr_number = pr["number"]
            pr_data = {
                "number": pr_number,
                "author": pr["user"]["login"],
                "created_at": pr["created_at"],
                "closed_at": pr.get("closed_at"),  # Use get() to avoid KeyError
                "state": pr["state"]
            }

            # ✅ Fetch actual submitted reviews (not just requested reviewers)
            reviews_url = f"https://api.github.com/repos/{self.repo}/pulls/{pr_number}/reviews"
            reviews_response = requests.get(reviews_url, headers=self.headers)
            if reviews_response.status_code == 200:
                reviews = reviews_response.json()
                reviewers = list({
                    review["user"]["login"]
                    for review in reviews
                    if review.get("user") and review.get("state") == "APPROVED"
                })
                pr_data["reviewers"] = reviewers

            self.db.store_pr(pr_data)

        return prs
