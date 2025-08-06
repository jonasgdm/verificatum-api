from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.align import Align
import requests
import questionary
from services.verificatum_api import post_keygen, get_publickey
from screens import home
from screens.sim import mock

console = Console()


def show():
    console.clear()

    painel_explicacao = Panel(
        Align.left(
            """
[white]Nesta etapa, cada servidor da mixnet gera sua parcela da chave privada, e juntos constroem uma chave pública compartilhada, que será usada para cifrar os votos.[/white]

[bold]Etapas realizadas:[/bold]
• Cada nó executa o algoritmo de geração de chaves (vmn -keygen).
• As parcelas privadas permanecem locais e secretas.
• A chave pública resultante é compartilhada e idêntica entre os nós.
• Essa chave será utilizada para cifragem dos votos simulados.

[bold]Importante:[/bold] A decifração dos votos só poderá ocorrer com a colaboração de um número mínimo de servidores, definido pelo parâmetro [bold]threshold[/bold] configurado no setup.
"""
        ),
        title="[bold blue]Passo 2 - Geração de Chave Pública[/bold blue]",
        border_style="blue",
        width=100,
        padding=(1, 2),
    )
    console.print(painel_explicacao)

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
        console.print(
            Panel(
                Align.left(chave.strip()),
                title="[bold]Chave Pública da Eleição[/bold]",
                border_style="green",
                width=100,
                padding=(1, 2),
            )
        )
        input("[CONTINUAR]")
        return mock.show()
    else:
        console.print("\n[bold red]Erro na geração da chave com /keygen[/bold red]")
        return False
