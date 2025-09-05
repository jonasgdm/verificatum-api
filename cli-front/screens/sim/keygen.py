from rich import print
from rich.console import Console

from services.verificatum_api import post_keygen, get_publickey

from ui.panel import shell
from ui.prompt import select
from ui.spinner import run_with_spinner

console = Console()


def show(_=None):
    console.clear()

    title = "[bold blue]Passo 2 - Geração de Chave Pública[/bold blue]"
    txt = """
[white]Nesta etapa, cada servidor da mixnet gera sua parcela da chave privada, e juntos constroem uma chave pública compartilhada, que será usada para cifrar os votos.[/white]

[bold]Etapas realizadas:[/bold]
• Cada nó executa o algoritmo de geração de chaves (vmn -keygen).
• As parcelas privadas permanecem locais e secretas.
• A chave pública resultante é compartilhada e idêntica entre os nós.
• Essa chave será utilizada para cifragem dos votos simulados.

[bold]Importante:[/bold] A decifração dos votos só poderá ocorrer com a colaboração de um número mínimo de servidores, definido pelo parâmetro [bold]threshold[/bold] configurado no setup.
"""
    console.print(shell(title, txt))

    escolha = select(
        "Deseja gerar a chave pública da eleição?",
        choices=["1. Iniciar KeyGen", "0. Voltar"],
    )

    if not (escolha.startswith("1")):
        console.print("[italic]Key generation cancelada.[/italic]")
        input("> Voltando...")
        return "home", None

    response = run_with_spinner(lambda: post_keygen())

    if response and response.get("status").startswith("Keygen complete"):
        console.print("\n[bold green]✓ Keygen concluído com sucesso![/bold green]\n")
        chave = get_publickey()

        title = "[bold]Chave Pública da Eleição[/bold]"
        console.print(shell(title, chave.strip(), border_style="green"))
        input("[CONTINUAR]")
        return "sim.mock", None
    else:
        console.print("\n[bold red]Erro na geração da chave com /keygen[/bold red]")
        input("> Voltando...")
        return "home", None
