import json
import os
import logging
from collections import defaultdict
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def sample_data_harvester(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n [SampleDataAgent] Loading sample commit data from /data/commits.json")

    try:
        # Load commits
        with open(os.path.join("data", "commits.json"), "r") as f:
            commits = json.load(f)
        
        print(f" Loaded {len(commits)} commits")
        
        # Extract pull requests from commits
        pull_requests = []
        for commit in commits:
            if 'pull_request' in commit and commit['pull_request']:
                pr_data = commit['pull_request']
                # Add author from commit to the PR data
                pr_data['author'] = commit.get('author')
                pull_requests.append(pr_data)
        
        logger.info(f"✅ Extracted {len(pull_requests)} pull requests with review data")
        if pull_requests:
            logger.info(f"Sample PR: {json.dumps(pull_requests[0], indent=2, default=str)}")
        
        # Return the state with commits and pull_requests
        return {
            **state,
            "commits": commits,
            "pull_requests": pull_requests  # Include pull_requests in the state
        }
        
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}", exc_info=True)
        return {
            "commits": [],
            "pull_requests": [],
            "file_hotspots": {},
            "error": str(e)
        }
