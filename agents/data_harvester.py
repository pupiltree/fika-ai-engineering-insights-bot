import json
from pathlib import Path
from langchain_core.runnables import Runnable

class DataHarvesterAgent(Runnable):
    """LangChain Runnable to simulate GitHub data harvesting."""

    def __init__(self, filepath="seed/fake_github_events.json"):
        self.filepath = Path(filepath)

    def invoke(self, input=None):
        """Load static GitHub commit data from JSON."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"❌ Seed file not found: {self.filepath}")
        
        with open(self.filepath, "r") as f:
            data = json.load(f)

        print(f"✅ DataHarvesterAgent: Loaded {len(data)} events.")
        return data
