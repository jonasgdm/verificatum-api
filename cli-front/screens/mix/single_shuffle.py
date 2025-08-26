import os
import json
import requests
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from utils.electionConfig_parser import load_election_config
from services.flask_api import _post
from services import verificatum_api
from requests_toolbelt.multipart import decoder
from rich.table import Table
from collections import Counter

from screens import home
from screens.mix import final_tally, shuffle_result

console = Console()
TALLY_PATH = "output/tally.json"
DECRYPT_DIR = "decrypted"
os.makedirs(DECRYPT_DIR, exist_ok=True)


def carregar_tally():
    if not os.path.exists(TALLY_PATH):
        return {}
    with open(TALLY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def show():
    config = load_election_config()
    if not config:
        console.print(
            "[bold red]Arquivo electionConfig.json não encontrado.[/bold red]"
        )
        return

    elections = [e for e in config["options"] if e["candidates"] > 0]
    status = [False] * len(elections)
    tally = carregar_tally()
    while True:
        console.clear()

        console.print(
            Panel(
                f"[bold]Eleições Ativas:[/bold] {len(elections)}\n"
                f"[bold]Total de votos:[/bold] {config['anyVotes'] + config['conventionalVotes'] + config['doubleVotes']}\n"
                f"[bold]AnyVotes:[/bold] {config['anyVotes']} | [bold]Duplicados:[/bold] {config['doubleVotes']}",
                title="Resumo Geral",
                width=80,
            )
        )

        escolha = questionary.select(
            "O que deseja realizar?",
            choices=[
                "1. Executar Shuffle (misturar)",
                "2. Decifrar Votos",
                "3. Apuração Final",
                "4. Sair",
            ],
        ).ask()

        if escolha.startswith("1."):
            spinner = Spinner("dots", text=f"Executando shuffle...")
            with Live(spinner, refresh_per_second=10, transient=True):
                if execute_shuffle():
                    console.print(
                        "\n[bold green]Shuffle realizado com sucesso[/bold green]"
                    )
            shuffle_result.show()

        elif escolha.startswith("2."):
            spinner = Spinner("dots", text=f"Executando decifração...")
            with Live(spinner, refresh_per_second=10, transient=True):
                if execute_decrypt():
                    console.print(
                        f"\n[bold green]✓ Decifração concluída.[/bold green]\n"
                        "O arquivo foi salvo em 'decrypted/decrypted.native'.\n "
                        "Agora vá para [bold]Apuração Final[/bold] para ver os resultados.\n"
                    )
            input("\nPressione Enter para continuar...")

        elif escolha.startswith("3."):
            show_final_tally(tally)

        elif escolha.startswith("4."):
            console.print("[bold yellow]Saindo...[/bold yellow]")
            home.show()


def execute_shuffle():
    receive_resp = _post(f"/shuffle")
    if not (
        receive_resp and receive_resp.get("status") == "Ciphertexts received and copied"
    ):
        console.print("\n[bold red]Erro ao enviar ciphertexts.[/bold red]\n")
        return False

    shuffle_resp = verificatum_api._post("/shuffler/shuffle")
    if not (shuffle_resp and shuffle_resp.get("status") == "Shuffle complete"):
        console.print("\n[bold red]Erro ao realizar o shuffle.[/bold red]\n")
        return False
    return True


def execute_decrypt():
    try:
        decrypt_resp = requests.post("http://localhost:8080/guardian/decrypt")
        decrypt_resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição /decrypt: {e}")
        return False

    if not (decrypt_resp):
        console.print("\n[bold red]Erro ao realizar a decifração.[/bold red]\n")
        return False
    if decrypt_resp is None:
        return False

    multipart_data = decoder.MultipartDecoder.from_response(decrypt_resp)
    part = multipart_data.parts[0]  # assume que é 1 arquivo
    os.makedirs("decrypted", exist_ok=True)
    path = os.path.join("decrypted", f"decrypted.native")
    with open(path, "wb") as f:
        f.write(part.content)  # conteúdo limpo, sem headers
    return True


def show_final_tally(tally):
    final_tally.mostrar_apuracao_final(tally)
