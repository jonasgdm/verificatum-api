from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

import requests
import questionary

from services.verificatum_api import post_setup

from utils.protinfo_parser import parse_protinfo

from screens.sim import keygen

# from screens import keygen, home

console = Console()

# SERVICES = {
#     "Verificatum API": "http://localhost:8080",
#     "Backend Flask": "http://127.0.0.1:5000/api",
# }


# def check_service(name, url):
#     try:
#         r = requests.get(url, timeout=2)
#         return True
#     except requests.RequestException:
#         return False


def show():
    console.clear()
    # 1. PAINEL EXPLICATIVO INICIAL
    painel_explicacao = Panel(
        Align.left(
            """
[white]O setup inicializa a infraestrutura da mixnet, distribuindo e sincronizando a configuração entre os nós.[/white]

[bold]Etapas realizadas:[/bold]
• Criação da sessão criptográfica (ID e nome únicos).
• Geração de arquivos locais para cada nó da mixnet.
• Registro dos endpoints de comunicação (HTTP e Hint).
• Compartilhamento dos arquivos entre todos os nós.
• Fusão dos arquivos de configuração em um único protocolo (protInfo.xml).

Ao final, todos os nós terão uma configuração sincronizada, pronta para executar o protocolo com [bold]threshold[/bold] de decifração.
"""
        ),
        title="[bold blue]Passo 1 - Configuração da Rede[/bold blue]",
        border_style="blue",
        width=100,
        padding=(1, 2),
    )
    console.print(painel_explicacao)
    # console.print(
    #     "[bold cyan]Verificando conectividade com servidores...[/bold cyan]\n"
    # )
    #
    # status_lines = []
    # for name, url in SERVICES.items():
    #     spinner = Spinner("dots", text=f"Testando {name}...")
    #     with Live(spinner, refresh_per_second=10, transient=True):
    #         ok = check_service(name, url)
    #     symbol = "[green]✓[/green]" if ok else "[red]✗[/red]"
    #     status_lines.append(f"{symbol} {name} ({url})")

    # console.print(Panel("\n".join(status_lines), title="Status dos Serviços"), width=80)

    escolha = questionary.select(
        "Deseja iniciar o setup?",
        choices=["Iniciar Setup", "↩ Voltar"],
    ).ask()

    if escolha == "Iniciar Setup":

        # 2. FEEDBACK DE EXECUÇÃO
        # steps = [
        #     "Matando processos anteriores e liberando portas...",
        #     "Criando diretórios de sessão para os nós...",
        #     "Executando 'vmni -prot' para cada nó...",
        #     "Registrando nome, HTTP e Hint de cada nó...",
        #     "Compartilhando arquivos de configuração entre os nós...",
        #     "Executando merge final dos arquivos de protocolo...",
        # ]

        spinner = Spinner("dots", text="Executando configuração da rede de mixing...")
        with Live(spinner, refresh_per_second=10, transient=True):
            # for step in steps:
            #     console.log(f"[cyan]* {step}")
            response = post_setup()
        if response and response.get("status") == "Setup complete":
            console.print(
                "\n[bold green]✓ Infraestrutura inicializada com sucesso.[/bold green]\n"
            )
            console.print(
                "[white]A mixnet está pronta para operar com os seguintes parâmetros:[/white]\n"
            )

            info = parse_protinfo()

            partes = "\n".join(
                [
                    f"[green]{p['nome']}[/green]  [cyan]{p['http']}[/cyan]"
                    for p in info["partes"]
                ]
            )
            bloco = (
                f"[bold]Nome da Sessão:[/bold] {info['nome']} ({info['sid']})\n"
                f"[bold]Partes:[/bold] {info['numero_partes']} | [bold]Threshold[/bold]: {info['threshold']}\n"
                f"[bold]Grupo:[/bold] {info['grupo']}\n"
                f"[bold]Provas:[/bold] {info['provas']} | [bold]Hash:[/bold] {info['hash']}\n"
                f"[bold]PRG:[/bold] {info['prg']} | [bold]Desafio (RO):[/bold] {info['vbitlenro']} bits\n"
                f"[bold]Distância estatística:[/bold] {info['distancia_estatistica']}\n"
                f"[bold]Largura dos votos:[/bold] {info['largura_voto']} ({'vetorial' if info['largura_voto'] > 1 else 'padrão'})\n"
                f"[bold]Bulletin board:[/bold] {info['bulletin_board'].split('.')[-1]} | [bold]Max ciphertexts:[/bold] {info.get('maxciph', '0')}\n\n"
                f"[bold]Mix Servers:[/bold]\n{partes}"
            )
            console.print(Panel(bloco, title="Configuração do Protocolo", width=100))
            input("[CONTINUAR]")
            return keygen.show()
        else:
            console.print("\n[bold red]Erro ao executar o setup.[/bold red]\n")
            return False
    else:
        console.print("[italic]Setup cancelado.[/italic]")
        return home.show()
