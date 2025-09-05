from rich.console import Console

from ui.panel import shell


console = Console()


def show(_=None):
    console.clear()
    title = "[bold blue]Visão Geral – Por que usar Mixnets?[/bold blue]"
    intro_text = """
[white]Este sistema demonstra como é possível garantir anonimato e integridade em eleições digitais mesmo com mobilidade de eleitores.[/white]

[bold]Problema:[/bold] Com a possibilidade de votar fora da seção de origem, há risco de votos duplicados. Além disso, não há como detectar duplicações em tempo real, o que compromete a confiabilidade se não houver tratamento posterior. Também é necessário preservar o anonimato, mesmo em um ambiente distribuído.

[bold]Solução proposta:[/bold] Utilizamos uma arquitetura baseada em mixnets criptográficas (redes de embaralhamento) para quebrar a associação entre voto cifrado e ordem de chegada, preservando o anonimato do eleitor.
"""

    console.print(shell(title, intro_text))
    input("[CONTINUAR]")
    return "sim.sim_menu", None
