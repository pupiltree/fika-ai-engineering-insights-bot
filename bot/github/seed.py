# seed.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from bot.storage import save_event, init_db
import random
import datetime

FAKE_USERS = ['alice', 'bob', 'carol']
FAKE_EVENTS = [
    {'type': 'commit', 'author': 'alice', 'additions': 120, 'deletions': 10, 'files': 3, 'timestamp': '2024-06-01T10:00:00Z'},
    {'type': 'commit', 'author': 'bob', 'additions': 80, 'deletions': 20, 'files': 2, 'timestamp': '2024-06-01T11:00:00Z'},
    {'type': 'pr', 'author': 'carol', 'additions': 200, 'deletions': 50, 'files': 5, 'timestamp': '2024-06-01T12:00:00Z'},
]

def seed():
    init_db()
    for event in FAKE_EVENTS:
        save_event(event)
    print('Seeded fake GitHub events.')

if __name__ == '__main__':
    seed() 