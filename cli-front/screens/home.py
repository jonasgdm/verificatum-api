from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
import questionary
from sys import exit

from screens import tests
from screens.sim import descrp, mock, result
from screens.mix import shuffle_setup, single_shuffle

console = Console()


def show():
    titulo = "[bold cyan]AnyWhere Voting - Simulador de Processo Eleitoral[/bold cyan]"

    descricao = (
        "[white]Este aplicativo simula parte do processo de votação eletrônica com mobilidade.[/white]\n\n"
        "[white]A simulação é dividida em duas etapas principais:[/white]\n"
        "1. [bold]Simulação de Votação[/bold] — geração de votos simulados, duplicados e convencionais.\n"
        "2. [bold]Mixagem e Decifração[/bold] — embaralhamento criptográfico dos votos (mixnets) e sua apuração segura.\n\n"
        "[white]O objetivo é demonstrar um fluxo simplificado e auditável de votação anônima baseado em mixnets,[/white]\n"
        "[white]mantendo clareza e verificabilidade mesmo para especialistas que não dominam os detalhes criptográficos.[/white]"
    )

    painel = Panel(
        Align.center(f"{titulo}\n\n{descricao}", vertical="middle"),
        width=90,
        padding=(1, 4),
        border_style="cyan",
    )

    console.clear()
    console.print(painel)

    escolha = questionary.select(
        "Escolha uma etapa para iniciar:",
        choices=[
            "1. Simular Votação",
            "2. Mixagem e Decifração",
            "0. Sair",
        ],
    ).ask()

    if escolha.startswith("1"):
        return mock.show()
    elif escolha.startswith("2"):
        return shuffle_setup.show()
    elif escolha.startswith("0"):
        console.print("[red]Encerrando...[/red]")
        exit()
