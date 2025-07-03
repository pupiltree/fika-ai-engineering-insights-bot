#!/usr/bin/env python3
"""
Smoke test script for PowerBiz Developer Analytics
This script verifies that the core components work without external dependencies.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from powerbiz.agents.data_harvester import DataHarvesterAgent
        print("✅ DataHarvesterAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DataHarvesterAgent: {e}")
        return False
    
    try:
        from powerbiz.agents.diff_analyst import DiffAnalystAgent
        print("✅ DiffAnalystAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DiffAnalystAgent: {e}")
        return False
    
    try:
        from powerbiz.agents.insight_narrator import InsightNarratorAgent
        print("✅ InsightNarratorAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import InsightNarratorAgent: {e}")
        return False
    
    try:
        from powerbiz.slack_bot.app import SlackBot
        print("✅ SlackBot imported successfully")
    except Exception as e:
        print(f"❌ Failed to import SlackBot: {e}")
        return False
    
    return True

def test_agent_initialization():
    """Test that agents can be initialized."""
    print("\nTesting agent initialization...")
    
    try:
        from powerbiz.agents.data_harvester import DataHarvesterAgent
        agent = DataHarvesterAgent()
        assert agent.agent_name == "data_harvester"
        print("✅ DataHarvesterAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize DataHarvesterAgent: {e}")
        return False
    
    try:
        from powerbiz.agents.diff_analyst import DiffAnalystAgent
        agent = DiffAnalystAgent()
        assert agent.agent_name == "diff_analyst"
        print("✅ DiffAnalystAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize DiffAnalystAgent: {e}")
        return False
    
    return True

def test_demo_mode():
    """Test demo mode functionality."""
    print("\nTesting demo mode...")
    
    # Set demo mode
    os.environ["DEMO_MODE"] = "true"
    
    try:
        # Mock Slack environment variables
        os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
        os.environ["SLACK_SIGNING_SECRET"] = "test-secret"
        os.environ["SLACK_APP_TOKEN"] = "xapp-test-token"
        
        from powerbiz.slack_bot.app import SlackBot
        
        # Create bot instance
        with patch('powerbiz.database.db.init_db'):
            bot = SlackBot()
            print("✅ SlackBot created successfully in demo mode")
        
        # Test demo report generation
        async def test_demo_report():
            report = await bot._generate_demo_report("weekly", "test/repo")
            assert "repository" in report
            assert "metrics" in report
            assert "narrative" in report
            print("✅ Demo report generated successfully")
            return True
        
        # Run async test
        result = asyncio.run(test_demo_report())
        return result
        
    except Exception as e:
        print(f"❌ Demo mode test failed: {e}")
        return False

def test_database_models():
    """Test database models."""
    print("\nTesting database models...")
    
    try:
        from powerbiz.database.models import Repository, Developer, Commit, PullRequest
        
        # Test model creation (without database)
        repo = Repository(
            github_id=123,
            name="test-repo",
            full_name="test/repo",
            description="Test repository"
        )
        assert repo.name == "test-repo"
        print("✅ Database models work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def main():
    """Run all smoke tests."""
    print("🔥 PowerBiz Developer Analytics - Smoke Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_agent_initialization,
        test_database_models,
        test_demo_mode
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All smoke tests passed! The MVP is ready for submission.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before submission.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
