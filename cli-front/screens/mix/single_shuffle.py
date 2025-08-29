import json
import os
import requests
from rich.console import Console


from services.flask_api import _post
from services import verificatum_api
from requests_toolbelt.multipart import decoder
from utils.electionConfig_parser import load_election_config

from ui.panel import shell, shell_variant_2
from ui.prompt import select
from ui.spinner import run_with_spinner

from screens.mix import show_election_configs

console = Console()

DECRYPT_DIR = "decrypted"


os.makedirs(DECRYPT_DIR, exist_ok=True)


def show(_=None):
    decrypted = False
    config = load_election_config()
    if not config:
        console.print(
            "[bold red]Arquivo electionConfig.json não encontrado.[/bold red]"
        )
        input("Voltando...")
        return "home", None

    elections = [e for e in config["options"] if e["candidates"] > 0]

    while True:
        console.clear()
        title = "O shuffle (mixagem)"
        txt = (
            "- Cada voto é um [italic]ciphertext[/italic] (ElGamal, probabilístico).\n"
            "- Os votos entram em uma lista ordenada.\n"
            "- Cada servidor de mix:\n"
            "  • Recebe a lista cifrada.\n"
            "  • Aplica uma permutação aleatória (embaralha).\n"
            "  • Re-randomiza cada ciphertext.\n"
            "- Resultado: nova lista cifrada, sem ligação com a ordem original.\n"
            "- Nenhum voto removido ou alterado — apenas permutado e re-randomizado.\n"
            "- Cada servidor publica prova de correção (ZKP).\n"
            "- Segurança: basta 1 servidor honesto para preservar anonimato."
        )
        console.print(shell_variant_2(title, txt))
        console.print(show_election_configs.build_config_panel())

        escolha = select(
            "O que deseja realizar?",
            choices=[
                "1. Executar Shuffle (misturar)",
                "2. Decifrar Votos",
                "3. Visualizar Shuffle",
                "4. Apuração Final",
                "0. Sair",
            ],
        )

        if escolha.startswith("1"):
            run_with_spinner(lambda: execute_shuffle())
            console.print(
                f"\n[bold green]✓ Shuffle Conclu[ido].[/bold green]\n"
                "Vá para 'Visualizar Shuffle' e visualize o embaralhamento\n "
            )
            input("\nPressione Enter para continuar...")

        elif escolha.startswith("2."):
            run_with_spinner(lambda: execute_decrypt())
            console.print(
                f"\n[bold green]✓ Decifração concluída.[/bold green]\n"
                "O arquivo foi salvo em 'decrypted/decrypted.native'.\n "
                "Agora vá para [bold]Apuração Final[/bold] para ver os resultados.\n"
            )
            decrypted = True
            input("\nPressione Enter para continuar...")

        elif escolha.startswith("3."):
            return "mix.shuffle_result", None

        elif escolha.startswith("4."):
            return "mix.show_final_tally", decrypted

        elif escolha.startswith("0."):
            return "home", None


def execute_shuffle():
    # Primeiro ele envia pro verificatum
    # dpois ele mistura (2 passos)
    receive_resp = _post(f"/shuffle")
    if not (
        receive_resp and receive_resp.get("status") == "Ciphertexts received and copied"
    ):
        console.print("\n[bold red]Erro ao enviar ciphertexts.[/bold red]\n")
        input("Voltando...")
        return "home", None

    shuffle_resp = verificatum_api._post("/shuffler/shuffle")

    if not (shuffle_resp and shuffle_resp.get("status") == "Shuffle complete"):
        console.print("\n[bold red]Erro ao realizar o shuffle.[/bold red]\n")
        input("Voltando...")
        return "home", None


def execute_decrypt():
    try:
        decrypt_resp = requests.post("http://localhost:8080/guardian/decrypt")
        decrypt_resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição /decrypt: {e}")
        input("[VOLTAR]")
        return "home", None

    if not (decrypt_resp):
        console.print("\n[bold red]Erro ao realizar a decifração.[/bold red]\n")
        return "home", None

    multipart_data = decoder.MultipartDecoder.from_response(decrypt_resp)
    part = multipart_data.parts[0]  # assume que é 1 arquivo
    os.makedirs("decrypted", exist_ok=True)
    path = os.path.join("decrypted", f"decrypted.native")
    with open(path, "wb") as f:
        f.write(part.content)  # conteúdo limpo, sem headers
    return
