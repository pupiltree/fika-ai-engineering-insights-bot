from langchain_core.tools import tool
import requests

def fetch_github_events(repo:str,token:str):
    headers={"Authorization":f"token{token}"}
    url=f"https://api.github.com/repos/{repo}/commits"
    response=requests.get(url,headers)
    
    if response.status_code==200:
        return response.json()
    return {"Error":response.text}