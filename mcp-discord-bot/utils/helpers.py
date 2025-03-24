import json

def load_rules(path="rules/rules.json"):
    with open(path, "r") as f:
        return json.load(f)
