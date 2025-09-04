from ui.spinner import run_with_spinner
from services import flask_api, verificatum_api
from app import mock_election
from infra.encryptors.node_daemon import NodeDaemonEncryptor
from infra.encryptors.parallel_encryptor import ParallelEncryptPool
import json
from utils.electionConfig_parser import load_election_config
import time
import os
import requests
from utils import log_parser

from rich.console import Console

console = Console()


def post_ciphertexts(file_path: str):
    url = "http://localhost:8080/shuffler/receive-ciphertexts"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "text/plain")}
        resp = requests.post(url, files=files)
    return resp.json()


def show(_=None):
    print("benchmark")
    run_with_spinner(
        lambda: verificatum_api.post_setup(), text="Configurando setup do Guardian..."
    )
    console.print("[green]Setup do Guardian Concluído[/green]")
    run_with_spinner(lambda: verificatum_api.post_keygen(), "Criando chave pública...")
    config = load_election_config()
    hex_str = verificatum_api.get_publickey()
    key_bytes = bytes.fromhex(hex_str)
    key = json.dumps(list(key_bytes))

    encryptor = ParallelEncryptPool(
        key, script="encryptor/daemon_encrypt.js", pool_size=3, max_workers=4
    )
    app = mock_election.MockElection(key, config, encryptor)

    run_with_spinner(lambda: app.generate_plaintexts(10), "Cifrando Votos...")
    run_with_spinner(lambda: app.finalize_encryption(), "Cifrando Votos...")
    app.export_gavt("json")
    app.export_gavt("csv")
    app.export_ciphertexts_only()

    ok = run_with_spinner(
        lambda: flask_api.post_gavt("output/gavt.json"),
        text="Enviando para o backend...",
    )

    run_with_spinner(
        lambda: verificatum_api._post(
            "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
        ),
        text="Configurando rede de mistura...",
    )
    run_with_spinner(
        lambda: post_ciphertexts("output/bench_ciphertexts"),
        text="Enviando Ciphertexts...",
    )
    run_with_spinner(lambda: verificatum_api._post("/shuffler/shuffle"))

    # app.export_tally()
    logs = verificatum_api.get_log()
    sum = log_parser.parse_shuffle_summary(logs)
    print(sum["computation_ms"] / 1000)
    # print(logs)

    input()
    return "home", None
