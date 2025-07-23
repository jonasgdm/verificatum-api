from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
import questionary

from screens import setup, keygen, mock, mix_demo, shuffle, shuffle_setup

from sys import exit

console = Console()


def show():
    titulo = "[bold cyan]AnyWhere Voting - Simulação[/bold cyan]"
    descricao = (
        "[white]Simulação de parte de processo de votação com mobilidade; [/white]\n"
        "\n[white]Funcionalidades: geração de votos, detecção de duplicatas e mixing.[/white]"
    )

    painel = Panel(
        Align.center(f"{titulo}\n\n{descricao}", vertical="middle"),
        width=70,
        padding=(1, 4),
        border_style="cyan",
    )

    console.clear()
    console.print(painel)

    escolha = questionary.select(
        "Escolha uma opção para continuar:",
        choices=[
            "1. [SETUP]",
            "2. [KEYGEN]",
            "3. [MOCKAGEM DE VOTOS]",
            "4. [SHUFFLE SETUP]",
            "5. [MIXING]",
            "6. [SOBRE]",
            "0. [SAIR]",
        ],
    ).ask()

    if escolha == "1. [SETUP]":
        return setup.show()
    elif escolha == "2. [KEYGEN]":
        return keygen.show()
    elif escolha == "3. [MOCKAGEM DE VOTOS]":
        return mock.show()
    elif escolha == "4. [SHUFFLE SETUP]":
        return shuffle_setup.show()
    elif escolha == "5. [MIXING]":
        return shuffle.show()
    elif escolha == "6. [SOBRE]":
        pass
    elif escolha == "0. [SAIR]":
        console.print("[red]Encerrando...[/red]")
        exit()
