# screens/mock.py

import os
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
import questionary
import json
from services.MockElection import MockElection
from utils.protinfo_parser import load_file

from services import flask_api

# from services.mock_vote_service import (
#     generate_mock_votes,
# )  # serviço que você irá implementar
from utils.electionConfig_parser import load_election_config

console = Console()


def display_tally(election: MockElection):
    """Exibe o tally da eleição formatado com rich."""
    console.print("\n[bold yellow]Tally Final da Simulação[/bold yellow]\n")

    for cargo, votos in election.tally.items():
        table = Table(
            title=f"Tally - {cargo.upper()}",
            show_header=True,
            header_style="bold green",
        )
        table.add_column("Candidato", justify="center")
        table.add_column("Votos", justify="center")

        for candidato, count in votos.items():
            table.add_row(str(candidato), str(count))

        console.print(table)


def format_config(config):
    base = (
        f"[bold]Tipo de Eleição:[/bold] {config['type']}\n"
        f"[bold]Votos totais:[/bold] {config['anyVotes'] + config['doubleVotes'] + config['conventionalVotes']}\n"
        f"[bold]Any Votes:[/bold] {config['anyVotes']} | "
        f"[bold]Votos Convencionais:[/bold] {config['conventionalVotes']} | "
        f"[bold]Votos Duplicados:[/bold] {config['doubleVotes']} \n"
        f"[bold]Votos Nulos:[/bold] {config['nullVotes']} | "
        f"[bold]Votos Branco:[/bold] {config['blankVotes']} \n"
    )
    return base


def table_cargos(cargos):
    table = Table(title="Cargos Ativos", show_header=True, header_style="bold magenta")
    table.add_column("Cargo")
    table.add_column("Nº de Candidatos", justify="center")
    for cargo in cargos:
        if cargo["candidates"] != 0:
            table.add_row(cargo["contest"].capitalize(), str(cargo["candidates"]))
    return table


def show():
    console.clear()
    config = load_election_config()

    if not config:
        console.print(
            "[bold red]Arquivo electionConfig.json não encontrado![/bold red]"
        )

    console.print(Panel(format_config(config), title="Configuração da Eleição"))
    console.print(table_cargos(config["options"]))

    escolha = questionary.select(
        "Deseja gerar os votos simulados?",
        choices=["Gerar Votos", "↩ Voltar"],
    ).ask()

    if escolha == "Gerar Votos":
        spinner = Spinner("dots", text="Gerando votos simulados...")
        with Live(spinner, refresh_per_second=10, transient=True):
            # chave = load_file("logs/publicKey")
            # with open("../verificatum-demo/01/publicKey", "rb") as f:
            with open("../verificatum-demo/01/publicKey", "rb") as f:
                key_bytes = f.read()
                key = json.dumps(list(key_bytes))

            e = MockElection(key, config)
            e.simulate()
            display_tally(e)
        console.print(
            "\n[bold green]✓ Lista de AnyVotes disponível em output/ ![/bold green]"
        )
        input("[ENVIAR PARA SERVIDOR FLASK]")
        return flask_api.post_gavt("output/gavt.json")
    else:
        console.print("[italic]Operação cancelada.[/italic]")
        return False
