#!/usr/bin/env python3
"""Local development server for the Engineering Productivity MVP."""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.config import settings, logger
from src.data.database import db
from src.data.github_client import github_client
from src.chat.slack_bot import start_slack_bot


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'GEMINI_API_KEY',
        'GITHUB_TOKEN', 
        'SLACK_BOT_TOKEN',
        'SLACK_SIGNING_SECRET',
        'DEFAULT_REPO_OWNER',
        'DEFAULT_REPO_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("Please check your .env file or environment variables")
        return False
    
    return True


def test_connections():
    """Test connections to external services."""
    logger.info("Testing external connections...")
    
    # Test GitHub API
    if github_client.test_connection():
        logger.info("✅ GitHub API connection successful")
    else:
        logger.error("❌ GitHub API connection failed")
        return False
    
    # Test database
    try:
        stats = db.get_stats()
        logger.info(f"✅ Database connection successful (events: {stats.get('total_events', 0)})")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    return True


def print_startup_info():
    """Print startup information."""
    print("\n" + "="*60)
    print("🚀 ENGINEERING PRODUCTIVITY MVP")
    print("="*60)
    print(f"📊 Repository: {settings.default_repo_owner}/{settings.default_repo_name}")
    print(f"🤖 LLM Model: {settings.llm_model}")
    print(f"💾 Database: {settings.database_path}")
    print(f"🔍 Default lookback: {settings.default_lookback_days} days")
    print(f"🌐 Server: http://localhost:3000")
    print("="*60)
    print("\n📝 Slack Setup:")
    print("   1. Add slash command: /dev-report")
    print("   2. Request URL: http://localhost:3000/slack/events")
    print("   3. Test with: /dev-report weekly")
    print("\n🎯 Usage Examples:")
    print("   /dev-report                    # Weekly report for default repo")
    print("   /dev-report monthly            # Monthly report")
    print("   /dev-report weekly my-repo     # Weekly report for specific repo")
    print("   /dev-report daily owner/repo   # Daily report for owner/repo")
    print("\n" + "="*60 + "\n")


def main():
    """Main entry point for local development server."""
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test connections
    if not test_connections():
        logger.warning("Some connections failed - continuing anyway...")
    
    # Print startup info
    print_startup_info()
    
    # Start the Slack bot
    try:
        logger.info("Starting Slack bot...")
        start_slack_bot("auto", 3000)  # Auto-detect Socket vs HTTP mode
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()