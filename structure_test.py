#!/usr/bin/env python3
"""
Simple structure test for PowerBiz Developer Analytics
Tests that all files exist and have the correct structure.
"""

import os
import sys

def test_project_structure():
    """Test that all required files exist."""
    print("🔍 Testing project structure...")
    
    required_files = [
        "powerbiz/__init__.py",
        "powerbiz/__main__.py",
        "powerbiz/agents/__init__.py",
        "powerbiz/agents/base_agent.py", 
        "powerbiz/agents/data_harvester.py",
        "powerbiz/agents/diff_analyst.py",
        "powerbiz/agents/insight_narrator.py",
        "powerbiz/agents/workflow.py",
        "powerbiz/database/__init__.py",
        "powerbiz/database/db.py",
        "powerbiz/database/models.py",
        "powerbiz/github_api/__init__.py",
        "powerbiz/github_api/client.py",
        "powerbiz/github_api/harvester.py",
        "powerbiz/slack_bot/__init__.py",
        "powerbiz/slack_bot/app.py",
        "powerbiz/visualization/__init__.py",
        "powerbiz/visualization/charts.py",
        "powerbiz/visualization/reports.py",
        "seed_data/seed.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_data_harvester.py",
        "tests/test_diff_analyst.py",
        "requirements.txt",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        "README.md"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print(f"\n✅ All {len(required_files)} required files found!")
    return True

def test_key_implementations():
    """Test that key methods exist in the code."""
    print("\n🔍 Testing key implementations...")
    
    tests = [
        ("powerbiz/agents/data_harvester.py", ["class DataHarvesterAgent", "analyze_repository_data", "_calculate_dora_metrics"]),
        ("powerbiz/agents/diff_analyst.py", ["class DiffAnalystAgent", "analyze_code_churn", "forecast_metrics", "generate_influence_map"]),
        ("powerbiz/agents/insight_narrator.py", ["class InsightNarratorAgent", "generate_daily_report", "generate_weekly_report"]),
        ("powerbiz/slack_bot/app.py", ["class SlackBot", "handle_dev_report_command", "_generate_demo_report"]),
        ("seed_data/seed.py", ["create_sample_data", "def main"]),
        (".env.example", ["OPENAI_API_KEY", "GITHUB_TOKEN", "SLACK_BOT_TOKEN"]),
        ("docker-compose.yml", ["version:", "services:", "powerbiz:"]),
        ("Makefile", ["install:", "run:", "test:", "seed:"])
    ]
    
    all_passed = True
    
    for file_path, required_strings in tests:
        if not os.path.exists(file_path):
            print(f"❌ {file_path} not found")
            all_passed = False
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_strings = []
            for req_string in required_strings:
                if req_string not in content:
                    missing_strings.append(req_string)
            
            if missing_strings:
                print(f"❌ {file_path} missing: {', '.join(missing_strings)}")
                all_passed = False
            else:
                print(f"✅ {file_path} - all key components found")
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_passed = False
    
    return all_passed

def test_requirements():
    """Test that requirements.txt has all needed packages."""
    print("\n🔍 Testing requirements...")
    
    required_packages = [
        "langchain", "langgraph", "slack-bolt", "sqlalchemy", 
        "openai", "matplotlib", "plotly", "pytest"
    ]
    
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read().lower()
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print(f"✅ All required packages found in requirements.txt")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def main():
    """Run structure tests."""
    print("🏗️  PowerBiz Developer Analytics - Structure Test")
    print("=" * 55)
    
    tests = [
        test_project_structure,
        test_key_implementations, 
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Structure Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Project structure is complete! Ready for submission.")
        print("\n📋 Next steps for evaluators:")
        print("1. pip install -r requirements.txt")
        print("2. python seed_data/seed.py")
        print("3. Set environment variables in .env")
        print("4. python -m powerbiz")
        return 0
    else:
        print("⚠️  Some structure issues found. Please fix before submission.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
