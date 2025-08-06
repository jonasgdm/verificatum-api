from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.layout import Layout
from rich.table import Table
from rich.columns import Columns
import questionary

from screens import home
from screens.sim import setup

console = Console()


def show():
    titulo = "[bold blue]Etapa 1 – Simular Votação[/bold blue]"

    descricao = """
[white]
[bold]Frontend:[/bold] Gera e cifra os votos simulados (imita uma eleição).

[bold]Backend Flask:[/bold] Detecta duplicatas e envia para serem embaralhados.

[bold]Verificatum:[/bold] Biblioteca que implementa o protocolo de mixnet com provas criptográficas. Coordena o processo de embaralhamento.

[bold]Nós da Mixnet:[/bold] Servidores que de fato reembaralham os votos, removendo qualquer vínculo com a origem.
[/white]
"""

    painel_descricao = Panel(
        Align.left(descricao),
        title=titulo,
        border_style="blue",
        padding=(1, 4),
        width=90,
    )

    diagrama_textual = """
[bold white]
            +-----------------------------+
            |         Plataforma Local    |
            |  +----------+      +-------+|
            |  | Frontend | <--> | Flask ||
            |  +----------+      +-------+|
            +-----------------------------+
                           |
                           v
            +-----------------------------+
            |       Open Verificatum      |
            +-----------------------------+
                /                     \\
                /                       \\
+--------------------------+   +--------------------------+
|       Nó da Mixnet       |   |       Nó da Mixnet       |
+--------------------------+   +--------------------------+
[/bold white]
    """

    painel_diagrama = Panel(
        Align.center(diagrama_textual),
        title="[bold magenta]Esquema Visual da Arquitetura[/bold magenta]",
        border_style="magenta",
        width=90,
        padding=(1, 2),
    )

    console.clear()
    console.print(painel_descricao)
    console.print(painel_diagrama)

    escolha = questionary.select(
        "Como deseja continuar?",
        choices=[
            "1. Iniciar Etapa de Simulação",
            "0. Voltar ao menu principal",
        ],
    ).ask()

    if escolha.startswith("1"):

        setup.show()
    else:
        home.show()
