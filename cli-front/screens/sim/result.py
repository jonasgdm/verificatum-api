from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from services import MockElection
from rich.align import Align
from rich import box
import readchar
import json
import os
from utils import electionConfig_parser

from screens import home

# from utils.gavt_parser import load_ciphered_votes  # você criaria esse

import questionary

PREFIX = "00000000020000000002010000002100"

console = Console()


def display_tally_from_file(path="output/tally.json"):
    """Lê e exibe o tally da eleição a partir de um arquivo JSON."""
    if not os.path.exists(path):
        console.print(f"[bold red]Arquivo {path} não encontrado.[/bold red]")
        return

    with open(path, "r") as f:
        tally = json.load(f)

    console.print("\n[bold yellow]Tally Final da Simulação[/bold yellow]\n")

    for cargo, votos in tally.items():
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

    input("[↩ VOLTAR]")


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


def paginar_votos(path="output/gavt.json", por_pagina=5, pagina=0):
    with open(path, "r") as f:
        votos = json.load(f)

    config = electionConfig_parser.load_election_config()
    cargos = [op["contest"] for op in config["options"] if op["candidates"] > 0]

    total = len(votos)
    inicio = pagina * por_pagina
    fim = min(inicio + por_pagina, total)

    tabela = Table(title=f"Votos Cifrados [{inicio + 1}-{fim} de {total}]")
    tabela.add_column("TokenID", style="cyan", no_wrap=True)
    for cargo in cargos:
        tabela.add_column(cargo.capitalize(), style="white")

    for voto in votos[inicio:fim]:
        linha = [voto["tokenID"]]
        for c in voto["encryptedVotes"]:
            texto = c
            if texto.startswith(PREFIX):
                texto = "..." + texto[len(PREFIX) : 60]
            else:
                texto = texto[:60]
            linha.append(texto)
        tabela.add_row(*linha)

    console.clear()
    console.print(tabela)
    console.print("[dim]\[a] Anterior  [d] Próxima  [ENTER] Sair[/dim]")
    tecla = readchar.readkey()
    if tecla == "d" and fim < total:
        paginar_votos(path=path, por_pagina=por_pagina, pagina=pagina + 1)
    elif tecla == "a" and pagina > 0:
        paginar_votos(path=path, por_pagina=por_pagina, pagina=pagina - 1)


def show():
    while True:
        console.clear()
        panel = Panel(
            Align.left(
                """
[white]A eleição simulada foi concluída com sucesso. Votos foram gerados, cifrados com a chave pública da mixnet e processados para remover duplicatas.[/white]

[bold]Visualização:[/bold] É possível inspecionar os votos cifrados e o resultado parcial (tally) obtido diretamente dos dados simulados.

[blue]A próxima etapa simularia um ambiente de mixagem,[/blue] com foco em embaralhamento (mixing) e decifração segura usando os servidores da mixnet.
"""
            ),
            title="[bold blue]Fim da Simulação de Eleição[/bold blue]",
            border_style="blue",
            width=100,
            padding=(1, 2),
        )

        console.print(panel)
        escolha = questionary.select(
            "Selecione uma ação:",
            choices=[
                "1.Visualizar Tally",
                "2.Visualizar votos",
                "↩ Voltar",
            ],
        ).ask()

        if escolha.startswith("1"):
            # seu display_tally já renderiza bem
            display_tally_from_file()

        elif escolha.startswith("2"):
            votos = paginar_votos()

        else:
            home.show()
