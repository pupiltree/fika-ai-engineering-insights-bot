from langchain_core.tools import tool
from agents.diff_analyst import analyze_diff
from agents.narrator import narrate_insights
import requests


def fetch_github_events(repo:str,token:str):
    """fetch"""
    headers={"Authorization":f"token{token}"}
    url=f"https://api.github.com/repos/{repo}/commits"
    response=requests.get(url,headers)
    
    if response.status_code==200:
        return response.json()
    return {"Error":response.text}

response=fetch_github_events("vnshrwt27/fika-ai-engineering-insights-bot.git","")
data=analyze_diff(response)
ans=narrate_insights(data)