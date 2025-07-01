from fika_agents.workflow import FikaWorkflow
from fika_db import database

if __name__ == "__main__":
    database.init_db()
    
    # Create and run the LangGraph workflow
    workflow = FikaWorkflow()
    summary = workflow.run_weekly_report()
    
    print("\n=== Engineering Productivity Summary (LangGraph) ===\n")
    print(summary)
