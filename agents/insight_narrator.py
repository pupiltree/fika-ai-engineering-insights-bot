# agents/insight_narrator.py
import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage

class InsightNarratorAgent:
    def __init__(self):
        self.name = "InsightNarrator"
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            model="mistralai/mistral-7b-instruct:free"
        )

    def run(self, state: Dict) -> Dict:
        commits = state.get("commits", [])
        analysis = state.get("churn_analysis", {})
        dora = state.get("dora_metrics", {})
        pr_stats = state.get("pr_stats", {})
        after_hours = state.get("after_hours_commits", 0)
        risky_count = state.get("risky_commit_count", 0)
        top_contributors = sorted(state.get("author_metrics", {}).items(), key=lambda x: x[1]["commits"], reverse=True)[:3]
        top_contrib_names = [a[0] for a in top_contributors]
        prompt = f"""
You are an engineering insights generator. Summarize this activity:

- Repo: {state.get('repo')}
- Total Commits: {len(commits)}
- Average Churn: {analysis.get('avg_churn', 0)}
- Risky Commits: {risky_count}
- After-hours Commits: {after_hours}
- Top Contributors: {top_contrib_names}
- DORA Metrics: {dora}
- PR Stats: {pr_stats}

Output a weekly engineering report in markdown format. Highlight risky and after-hours work, and summarize DORA metrics.
"""
        result = self.llm([
            SystemMessage(content="You are a concise engineering analyst."),
            HumanMessage(content=prompt)
        ])
        return {**state, "narrative": result.content}
