import os
import json

CONFIG_PATH = "electionConfig.json"


def load_election_config():
    if not os.path.exists(CONFIG_PATH):
        return None

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    parsed = {
        "type": data.get("type"),
        "totalVotes": data.get("totalVotes"),
        "numberBallots": data.get("numberBallots"),
        "anyVotes": data.get("anyVotes"),
        "doubleVotes": data.get("doubleVotes"),
        "blankVotes": data.get("blankVotes"),
        "nullVotes": data.get("nullVotes"),
        "options": data.get("options"),
    }
    return parsed
