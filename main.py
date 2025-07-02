import os
from dotenv import load_dotenv

from agents.data_harvester import DataHarvesterAgent
from agents.diff_analyzer import DiffAnalyzerAgent
from agents.insight_narrator import InsightNarratorAgent

# 🔧 Load .env file
load_dotenv()

def run_pipeline(repo: str):
    print("\n🚀 Starting Engineering Productivity Insight Pipeline...\n")

    # 1. Run Data Harvester
    data_agent = DataHarvesterAgent()
    github_data = data_agent.run({"repo": repo})

    # 2. Run Diff Analyzer
    diff_agent = DiffAnalyzerAgent()
    analysis_data = diff_agent.run(github_data)

    # 3. Run Insight Narrator
    insight_agent = InsightNarratorAgent()
    merged_state = {**github_data, **analysis_data}
    insights = insight_agent.run(merged_state)

    # 4. Print or save the final insight report
    print("\n===== Engineering Report =====\n")
    print(insights.get('narrative', '❌ No narrative generated.'))

    # Save to file
    with open("output/engineering_report.txt", "w", encoding="utf-8") as f:
        f.write(insights.get('narrative', 'No narrative'))

if __name__ == "__main__":
    repo = os.getenv("GITHUB_REPO", "mock-org/mock-repo")
    print(f"🔍 Repo to analyze: {repo}")
    run_pipeline(repo)
