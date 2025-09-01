from rich.console import Console

from ui.panel import shell
from ui.prompt import select

console = Console()


def show(_=None):
    title = "[bold cyan]AnyWhere Voting - Simulador de Processo Eleitoral[/bold cyan]"

    description = (
        "[white]Este aplicativo simula parte do processo de votação eletrônica com mobilidade.[/white]\n\n"
        "[white]A simulação é dividida em duas etapas principais:[/white]\n"
        "1. [bold]Simulação de Votação[/bold] — geração de votos simulados, duplicados e convencionais.\n"
        "2. [bold]Mixagem e Decifração[/bold] — embaralhamento criptográfico dos votos (mixnets) e sua apuração segura.\n\n"
        "[white]O objetivo é demonstrar um fluxo simplificado e auditável de votação anônima baseado em mixnets,[/white]\n"
        "[white]mantendo clareza e verificabilidade mesmo para especialistas que não dominam os detalhes criptográficos.[/white]"
    )

    console.clear()
    console.print(shell(title, description))

    escolha = select(
        "Escolha uma etapa para iniciar:",
        [
            "1. Simular Votação",
            "2. Mixagem e Decifração",
            "3. Benchmarking",
            "0. Sair",
        ],
    )

    if escolha.startswith("1"):
        return "sim.descrp", None
    elif escolha.startswith("2"):
        return "mix.shuffle_setup", None
    elif escolha.startswith("3"):
        return "benchmark", None
    elif escolha.startswith("0"):
        console.print("[red]Encerrando...[/red]")
        return None, None
