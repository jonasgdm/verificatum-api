from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
import questionary

from screens import mock

from services.verificatum_api import post_keygen
from utils.protinfo_parser import load_file

from screens import mock, home

from services.verificatum_api import get_publickey

console = Console()


def show():
    console.clear()
    escolha = questionary.select(
        "Deseja gerar a chave pública da eleição?",
        choices=["Iniciar KeyGen", "↩ Voltar"],
    ).ask()

    if escolha != "Iniciar KeyGen":
        console.print("[italic]Key generation cancelada.[/italic]")
        return home.show()

    spinner = Spinner("dots", text="Gerando chave com /keygen...")
    with Live(spinner, refresh_per_second=10, transient=True):
        response = post_keygen()

    if response and response.get("status") == "Keygen complete":
        console.print("\n[bold green]✓ Keygen concluído com sucesso![/bold green]\n")
        chave = get_publickey()
        console.print(Panel(chave.strip(), title="Chave Pública da Eleição"), width=80)
        input("[CONTINUAR]")
        return mock.show()
    else:
        console.print("\n[bold red]Erro na geração da chave com /keygen[/bold red]")
        return False
