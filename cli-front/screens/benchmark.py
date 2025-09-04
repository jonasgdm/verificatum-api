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
import csv

console = Console()

bench_sizes = [100, 500, 1000, 5000, 10000]
results = []
csv_path = "output/benchmark_results.csv"


def post_ciphertexts(file_path: str):
    url = "http://localhost:8080/shuffler/receive-ciphertexts"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "text/plain")}
        resp = requests.post(url, files=files)
    return resp.json()


def setup_guardian():
    response_setup = run_with_spinner(
        lambda: verificatum_api.post_setup(), text="Inicializando setup..."
    )
    if response_setup and response_setup.get("status") == "Setup complete":
        console.print("\n[bold green]✓ DONE[/bold green]")
    else:
        return False

    response_keygen = run_with_spinner(
        lambda: verificatum_api.post_keygen(), text="Gerando Chave Pública"
    )

    if response_keygen and response_keygen.get("status") == "Keygen complete":
        console.print("\n[bold green]✓ DONE[/bold green]")
    else:
        return False
    return True


def setup_election_configs():
    config = load_election_config()
    hex_str = verificatum_api.get_publickey()
    key_bytes = bytes.fromhex(hex_str)
    key = json.dumps(list(key_bytes))

    encryptor = ParallelEncryptPool(
        key, script="encryptor/daemon_encrypt.js", pool_size=3, max_workers=4
    )
    app = mock_election.MockElection(key, config, encryptor)
    # run_with_spinner(lambda: app.generate_plaintexts(n_plaintexts), "Cifrando Votos...")
    # run_with_spinner(lambda: app.finalize_encryption(), "Cifrando Votos...")
    # app.export_gavt("json")
    # app.export_gavt("csv")
    # app.export_ciphertexts_only()
    return app


def show(_=None):
    print("benchmark")
    if not (setup_guardian()):
        console.print("[red]Erro no setup[/red]")

    for n in bench_sizes:
        run_with_spinner(
            lambda: verificatum_api._post(
                "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
            ),
            text="Configurando rede de mistura...",
        )
        console.print(f"[blue]Rodando benchmark com {n} plaintexts...[/blue]")
        app = setup_election_configs()
        app.generate_plaintexts(n)
        app.finalize_encryption()
        app.export_ciphertexts_only("output/ciphertexts")

        post_ciphertexts("output/ciphertexts")
        verificatum_api._post("/shuffler/shuffle")

        logs = verificatum_api.get_log()
        summary = log_parser.parse_shuffle_summary(logs)
        elapsed = summary["computation_ms"] / 1000
        proof_size = summary.get("proof_size_bytes")

        results.append(
            {
                "n_plaintexts": n,
                "elapsed_s": elapsed,
                "throughput": n / elapsed,
                "proof_size_bytes": proof_size,
            }
        )

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        console.print(f"[green]✓ Resultado salvo após {n} votos[/green]")
