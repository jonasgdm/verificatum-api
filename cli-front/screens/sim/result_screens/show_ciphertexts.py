from collections import Counter
import json
from ui.paginate import paginate_table
from utils import electionConfig_parser

PREFIX = "00000000020000000002010000002100"


def _shorten(cipher: str) -> str:
    # mantém prefixo reconhecível; se bater com PREFIX, corta o começo
    if cipher.startswith(PREFIX):
        return "..." + cipher[len(PREFIX) : 60]
    return cipher[:60]


def paginar_votos(path="output/gavt.json", por_pagina=5):
    with open(path, "r") as f:
        votos = json.load(f)

    config = electionConfig_parser.load_election_config()
    cargos = [op["contest"] for op in config["options"] if op["candidates"] > 0]

    # contagem por token p/ destacar duplicados
    token_counts = Counter(v["tokenID"] for v in votos)

    # monta headers e rows
    headers = ["TokenID"] + [c.capitalize() for c in cargos]
    rows = []
    for v in votos:
        linha = [v["tokenID"]] + [_shorten(c) for c in v["encryptedVotes"]]
        rows.append(linha)

    def title_fn(i1, i2, total):
        return f"Votos Cifrados [{i1}-{i2} de {total}]"

    def highlight_fn(idx_global):
        token = votos[idx_global]["tokenID"]
        return "bold red" if token_counts[token] > 1 else None

    paginate_table(
        headers=headers,
        rows=rows,
        title_fn=title_fn,
        page_size=por_pagina,
        highlight_fn=highlight_fn,
    )
