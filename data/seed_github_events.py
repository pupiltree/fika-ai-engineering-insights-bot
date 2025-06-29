import random, json

def seed_events():
    fake_events = [
        {'author': 'alice', 'additions': 100, 'deletions': 20, 'changed_files': 5, 'sha': 'abc123'},
        {'author': 'bob', 'additions': 50, 'deletions': 10, 'changed_files': 2, 'sha': 'def456'},
        # ... more events
    ]
    with open('seed_events.json', 'w') as f:
        json.dump(fake_events, f)
