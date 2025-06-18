from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console

import questionary
from questionary import Style

import sys

console = Console()

custom_style = Style(
    [
        (
            "highlighted",
            "fg:#000000 bg:#00ff00",
        ),  # Cor do item sob a seta ← destaque real
    ]
)


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
        choices=["[Iniciar]", "[Sobre]", "[Sair]"],
        style=custom_style,
    ).ask()

    if escolha == "[Iniciar]":
        return True
    elif escolha == "[Sobre]":
        console.print(
            "\n[italic]Sistema experimental baseado em tokens, mixnets e criptografia homomórfica.[/italic]"
        )
        input("\nPressione Enter para voltar.")
        return show()
    else:
        console.print("[red]Encerrando...[/red]")
        sys.exit()
