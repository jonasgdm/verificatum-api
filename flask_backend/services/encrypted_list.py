import json
import os

BASE = os.path.join(os.path.dirname(__file__), "encrypted_outputs")


def save_lists_by_contest(lists_by_index):
    os.makedirs(BASE, exist_ok=True)

    for idx, lista in lists_by_index.items():
        path = os.path.join(BASE, f"contest_{idx}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lista, f, indent=2)
