from rich.panel import Panel
from rich.align import Align
from rich.console import Console

from screens.sim import sim_menu

console = Console()


def show():
    console.clear()
    intro_text = """
[white]Este sistema demonstra como é possível garantir anonimato e integridade em eleições digitais mesmo com mobilidade de eleitores.[/white]

[bold]Problema:[/bold] Com a possibilidade de votar fora da seção de origem, há risco de votos duplicados. Além disso, não há como detectar duplicações em tempo real, o que compromete a confiabilidade se não houver tratamento posterior. Também é necessário preservar o anonimato, mesmo em um ambiente distribuído.

[bold]Solução proposta:[/bold] Utilizamos uma arquitetura baseada em mixnets criptográficas (redes de embaralhamento) para quebrar a associação entre voto cifrado e ordem de chegada, preservando o anonimato do eleitor.
"""

    painel_introducao = Panel(
        Align.left(intro_text),
        title="[bold blue]Visão Geral – Por que usar Mixnets?[/bold blue]",
        border_style="blue",
        width=100,
        padding=(1, 4),
    )
    console.print(painel_introducao)
    input("[CONTINUAR]")
    sim_menu.show()
