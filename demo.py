#!/usr/bin/env python3
"""
Demo script showing the complete FIKA AI Engineering Productivity Bot workflow.
"""

import time
from fika_agents.workflow import FikaWorkflow
from fika_db import database

def main():
    print(" FIKA AI Engineering Productivity Bot Demo")
    print("=" * 50)
    
    # Initialize database
    print("Initializing database...")
    database.init_db()
    
    # Create workflow
    print("Creating LangGraph workflow...")
    workflow = FikaWorkflow()
    
    # Show agent architecture
    print("\n Agent Architecture:")
    print("  DataHarvester → DiffAnalyst → InsightNarrator")
    print("       ↓              ↓              ↓")
    print("  GitHub Data   Code Analysis   DORA Narratives")
    
    # Run workflow step by step
    print("\n Running LangGraph Workflow...")
    print("  Step 1: DataHarvester fetching GitHub data...")
    time.sleep(1)
    
    print("  Step 2: DiffAnalyst analyzing code churn...")
    time.sleep(1)
    
    print("  Step 3: InsightNarrator generating summary...")
    time.sleep(1)
    
    # Get results
    summary = workflow.run_weekly_report()
    
    print("\n Weekly Engineering Productivity Report:")
    print("-" * 50)
    print(summary)
    
    print("\n Demo Complete!")
    print(" Try this in Slack: `/dev-report weekly`")

if __name__ == "__main__":
    main() 