import json

def load_seed_data():
    with open("data/seed_data.json", "r") as f:
        return json.load(f)
