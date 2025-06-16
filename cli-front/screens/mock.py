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

# from services.mock_vote_service import (
#     generate_mock_votes,
# )  # serviço que você irá implementar
from services.electionConfig_parser import load_election_config

console = Console()


def format_config(config):
    base = (
        f"[bold]Tipo de Eleição:[/bold] {config['type']}\n"
        f"[bold]Votos totais:[/bold] {config['totalVotes']}\n"
        f"[bold]Any Votes:[/bold] {config['anyVotes']} | [bold]Votos Convencionais:[/bold] {config["totalVotes"] - config["anyVotes"]} \n"
        f"[bold]Votos Nulos:[/bold] {config['nullVotes']} | [bold]Votos Branco:[/bold] {config["blankVotes"]} \n"
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
            # generate_mock_votes(config)
            return
        console.print(
            "\n[bold green]✓ Votos simulados gerados com sucesso![/bold green]"
        )
    else:
        console.print("[italic]Operação cancelada.[/italic]")
