import json
import os

def test_fake_data_loads():
    path = os.path.join("src", "seed", "seedData", "fake_commits.json")
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert "sha" in data[0]  # adjust to match your schema
