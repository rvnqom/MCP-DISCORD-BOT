import json

def load_rules(path):
    with open(path, "r") as f:
        return json.load(f)
