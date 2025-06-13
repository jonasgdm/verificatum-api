import json
import os

DUPLICATE_VOTES_FILE = os.path.join(os.path.dirname(__file__), "duplicated_votes.json")

DuplicatedVotesTable = []


def save_duplicate_votes():
    with open(DUPLICATE_VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(DuplicatedVotesTable, f, indent=2, ensure_ascii=False)


def load_duplicate_votes():
    global DuplicatedVotesTable
    if os.path.exists(DUPLICATE_VOTES_FILE):
        with open(DUPLICATE_VOTES_FILE, "r", encoding="utf-8") as f:
            DuplicatedVotesTable = json.load(f)
