from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.spinner import Spinner
from rich.live import Live
import questionary
import requests
from utils.electionConfig_parser import load_election_config
from services.verificatum_api import _post

from screens import home, shuffle

console = Console()


def show():
    config = load_election_config()
    if not config:
        console.print(
            "[bold red]Arquivo electionConfig.json não encontrado.[/bold red]"
        )
        return

    elections = config["options"]

    console.clear()

    console.print(
        Panel(
            f"[bold]Eleições Ativas:[/bold] {len(elections)}\n"
            f"[bold]Total de votos:[/bold] {config['anyVotes'] + config['conventionalVotes'] + config['doubleVotes']}\n"
            f"[bold]AnyVotes:[/bold] {config['anyVotes']} | "
            f"[bold]Duplicados:[/bold] {config['doubleVotes']}\n",
            title="Resumo Geral",
            width=80,
        )
    )
    escolha = questionary.select(
        "Iniciar setup:",
        choices=["[SETUP SHUFFLER]", "[↩ VOLTAR]"],
    ).ask()

    if escolha == "[SETUP SHUFFLER]":
        spinner = Spinner("dots", text="Fazendo setup do shuffler...")
        with Live(spinner, refresh_per_second=10, transient=True):
            response = _post(
                "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
            )
        print(response)
        if response and response.get("status") == "Shuffler setup complete":
            console.print(
                "\n[bold green]✓ Shuffler Setup concluído com sucesso![/bold green]\n"
            )
            input("[CONTINUAR]")
            return shuffle.show()
        else:
            return False

    elif escolha == "[↩ VOLTAR]":
        return home.show()

    else:
        console.print("\n[bold red]Erro na geração da chave com /keygen[/bold red]")
        return False
