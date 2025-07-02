from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
print("Loaded token:", token[:10])  # Just first 10 chars

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

res = requests.get("https://api.github.com/user", headers=headers)
print("✅ GitHub Response:", res.status_code)
print(res.json())
