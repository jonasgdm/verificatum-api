import random
from collections import defaultdict
from storage.duplicate_vote_table_storage import (
    DuplicatedVotesTable,
    save_duplicate_votes,
)


def process_gavt(gavt):
    # 1. ordenar por tokenID
    gavt.sort(key=lambda v: v["tokenID"])

    # 2. agrupar por tokenID
    grouped = defaultdict(list)
    for vote in gavt:
        grouped[vote["tokenID"]].append(vote)

    # 3. selecionar 1 aleatório entre duplicados
    selected_votes = []
    for tokenID, votes in grouped.items():
        if len(votes) > 1:
            selected_votes.append(random.choice(votes))

    # 4. salvar na DuplicatedVotesTable
    DuplicatedVotesTable.clear()
    DuplicatedVotesTable.extend(selected_votes)
    save_duplicate_votes()

    return {
        "totalDuplicados": len(selected_votes),
        "tokenIDsComDuplicata": list(grouped.keys()),
    }
