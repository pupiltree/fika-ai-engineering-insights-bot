from agents.data_harvester import fetch_github_events
from agents.diff_analyst import analyze_diff
from agents.narrator import narrate_insights

events=fetch_github_events("vnshrwt27/fika-ai-engineering-insights-bot","")
churn_data=analyze_diff(events)
res=narrate_insights(churn_data)
print(res)