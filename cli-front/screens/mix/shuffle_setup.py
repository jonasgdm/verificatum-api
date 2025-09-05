from rich.console import Console

from utils.electionConfig_parser import load_election_config
from services.verificatum_api import _post

from ui.panel import shell
from ui.prompt import select
from ui.spinner import run_with_spinner

from screens.mix import show_election_configs


console = Console()


def show(_=None):
    config = load_election_config()
    if not config:
        console.print(
            "[bold red]Arquivo electionConfig.json não encontrado.[/bold red]"
        )
        input("Voltando...")
        return "home", None

    console.clear()
    title = "[bold blue]Etapa de Embaralhamento (Mixnet)[/bold blue]"
    txt = """[white]
Os votos cifrados agora serão embaralhados para garantir o anonimato.

Isso impede que se descubra a ordem em que chegaram ou quem votou em quem.
Usamos uma rede com múltiplos servidores para executar essa etapa de forma segura, reutilizando a mesma chave pública usada na cifragem.

Após o embaralhamento, os votos embaralhados seguem para a próxima fase da apuração.
[/white]"""
    console.print(shell(title, txt))
    console.print(show_election_configs.build_config_panel())

    escolha = select(
        "Iniciar :",
        choices=["1. Configurar Rede de Mixagem", "[↩ VOLTAR]"],
    )

    if escolha.startswith("1"):
        response = run_with_spinner(
            lambda: _post(
                "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
            ),
            text="Configurando rede de mistura...",
        )
        if response and response.get("status") == "Shuffler setup complete":
            console.print(
                "\n[bold green]✓ Rede de mistura devidamente configurada![/bold green]\n"
            )
            input("[CONTINUAR]")
            return "mix.single_shuffle", None
        else:
            console.print("[red]Erro ao inicializar o Shuffler[/red]")
            input("Voltando...")
            return "home", None

    elif escolha == "[↩ VOLTAR]":
        return "home", None
