# data_harvester/json_storage.py
import json
import os

def load_json_if_exists(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = f.read()
                return json.loads(data)
        except json.JSONDecodeError:
            print(f"⚠️ Could not decode {path}")
            return []
    return []

