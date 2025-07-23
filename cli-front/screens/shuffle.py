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

        abas = []
        for i, eleicao in enumerate(elections):
            tick = "✅" if status[i] else ""
            titulo = f"{tick} {eleicao['contest'].capitalize()}"
            abas.append(titulo)

        idx = questionary.select(
            "Selecione uma eleição para shufflear:",
            choices=[f"{i} - {abas[i]}" for i in range(len(abas))] + ["↩ Voltar"],
        ).ask()

        if idx == "↩ Voltar":
            return

        index = int(idx.split(" - ")[0])
        cargo = elections[index]["contest"]

        confirm = questionary.confirm(
            f"Executar shuffle e decrypt da eleição {cargo}?"
        ).ask()
        if not confirm:
            continue

        spinner = Spinner("dots", text=f"Executando shuffle e decrypt '{cargo}'...")
        with Live(spinner, refresh_per_second=10, transient=True):
            # 1. mandar listas p Shuffle
            receive_resp = _post(f"/shuffle/{index}")
        if not (
            receive_resp
            and receive_resp.get("status") == "Ciphertexts received and copied"
        ):
            console.print("\n[bold red]Erro ao enviar ciphertexts.[/bold red]\n")
            return False

        console.print(
            "\n[bold green]Ciphertexts recebidos pelo verificatum[/bold green]"
        )

        input("> [SHUFFLE]")
        spinner = Spinner("dots", text=f"Executando shuffle de '{cargo}'...")
        with Live(spinner, refresh_per_second=10, transient=True):
            # 2. Decrypt
            shuffle_resp = verificatum_api._post("/shuffler/shuffle")
        print(shuffle_resp)
        if not (shuffle_resp and shuffle_resp.get("status") == "Shuffle complete"):
            console.print("\n[bold red]Erro ao realizar o shuffle.[/bold red]\n")
            return False
        console.print("\n[bold green]Shuffle realizado com sucesso[/bold green]")

        input("> [DECRYPT]")
        spinner = Spinner("dots", text=f"Executando decrypt de '{cargo}'...")
        with Live(spinner, refresh_per_second=10, transient=True):
            try:
                decrypt_resp = requests.post("http://localhost:8080/guardian/decrypt")
                decrypt_resp.raise_for_status()
            except requests.RequestException as e:
                print(f"[Erro] Falha na requisição /decrypt: {e}")
                return None

        if not (decrypt_resp):
            console.print("\n[bold red]Erro ao realizar a decifração.[/bold red]\n")
            return False

        # 3. Salvar decrypt

        if decrypt_resp is None:
            return None

        multipart_data = decoder.MultipartDecoder.from_response(decrypt_resp)
        part = multipart_data.parts[0]  # assume que é 1 arquivo
        path = os.path.join("decrypted", f"decrypted_{index}.native")
        with open(path, "wb") as f:
            f.write(part.content)  # conteúdo limpo, sem headers

        console.print(f"[✓] Decrypt salvo em: {path}")
        input(">..")

        # 1. Ler os votos do arquivo .native (já feito)
        with open(path, "r", encoding="utf-8") as f:
            decrypted_votes = [linha.strip() for linha in f if linha.strip()]

        # 2. Processar tally original e novo
        votos_originais = tally.get(cargo, {})
        tally_original = {str(k): int(v) for k, v in votos_originais.items()}
        tally_decrypt = Counter(decrypted_votes)

        # 3. Preparar tabela comparativa
        table = Table(title=f"Tally Comparativo - {cargo}", show_lines=True)
        table.add_column("Candidato", justify="center")
        table.add_column("Original", justify="center")
        table.add_column("Descartados", justify="center")
        table.add_column("Válidos", justify="center")

        todos_candidatos = set(tally_original.keys()).union(tally_decrypt.keys())

        for candidato in sorted(todos_candidatos):
            orig = tally_original.get(candidato, 0)
            novo = tally_decrypt.get(candidato, 0)
            diff = orig - novo
            table.add_row(candidato, str(orig), str(novo), str(diff))

        # 4. Totais
        total_original = sum(tally_original.values())
        total_decrypt = sum(tally_decrypt.values())
        total_descartados = total_original - total_decrypt

        # 5. Exibir
        console.clear()
        console.print(
            f"[bold cyan]📥 Resultado após shuffle e decrypt: {cargo}[/bold cyan]\n"
        )
        console.print(table)
        console.print(f"\n[bold]Total original:[/bold] {total_original}")
        console.print(f"[bold]Descartados:[/bold] {total_decrypt}")
        console.print(f"[bold red]Válidos:[/bold red] {total_descartados}\n")

        status[index] = True
        input("[CONTINUAR]")

        if all(status):
            cont = questionary.confirm(
                "Todas as eleições foram shuffleadas e decryptadas. Deseja continuar?"
            ).ask()
            if cont:
                break
