#!/usr/bin/env python3

"""
PowerBiz - AI-powered developer analytics MVP using LangChain + LangGraph agents
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    from powerbiz.slack_bot.app import start_slack_bot
    
    logger.info("Starting PowerBiz Developer Analytics")
    
    # Start the Slack bot application
    start_slack_bot()

if __name__ == "__main__":
    main()
