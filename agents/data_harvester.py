
import requests


def fetch_github_events(state):
    """fetch"""
    repo = state["repo"]
    token = state["token"]
    headers={"Authorization":f"token{token}"}
    url=f"https://api.github.com/repos/{repo}/commits"
    response=requests.get(url,headers)
    
    if response.status_code==200:
        
        return {**state, "commits": response.json()}
    return {"Error":response.text}

