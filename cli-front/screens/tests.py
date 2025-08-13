from services.MockElection import MockElection
from services.verificatum_api import get_publickey
import json
from utils.electionConfig_parser import load_election_config

CONFIG_PATH = "electionConfig.json"


def show():
    config = load_election_config()

    hex_str = get_publickey()
    key_bytes = bytes.fromhex(hex_str)
    key = json.dumps(list(key_bytes))  # mesmo formato que você já usava
    e = MockElection(key, config)
    e.simulate()
    print(e.candidate_codes)
