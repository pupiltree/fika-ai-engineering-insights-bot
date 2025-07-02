from typing import TypedDict, List, Dict

class MyState(TypedDict):
    events: List[Dict]
    diff_summary: Dict
    insight: str
    author_stats: List[Dict]
