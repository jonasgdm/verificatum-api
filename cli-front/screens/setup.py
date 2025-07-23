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

from screens import keygen, home

console = Console()

SERVICES = {
    "Verificatum API": "http://localhost:8080",
    "Backend Flask": "http://127.0.0.1:5000/api",
}


def check_service(name, url):
    try:
        r = requests.get(url, timeout=2)
        return True
    except requests.RequestException:
        return False


def show():
    console.clear()
    console.print(
        "[bold cyan]Verificando conectividade com servidores...[/bold cyan]\n"
    )

    status_lines = []
    for name, url in SERVICES.items():
        spinner = Spinner("dots", text=f"Testando {name}...")
        with Live(spinner, refresh_per_second=10, transient=True):
            ok = check_service(name, url)
        symbol = "[green]✓[/green]" if ok else "[red]✗[/red]"
        status_lines.append(f"{symbol} {name} ({url})")

    console.print(Panel("\n".join(status_lines), title="Status dos Serviços"), width=80)

    escolha = questionary.select(
        "Deseja iniciar o setup?",
        choices=["Iniciar Setup", "↩ Voltar"],
    ).ask()

    if escolha == "Iniciar Setup":
        spinner = Spinner("dots", text="Executando /setup...")
        with Live(spinner, refresh_per_second=10, transient=True):
            response = post_setup()
        if response and response.get("status") == "Setup complete":
            console.print("\n[bold green]✓ Setup concluído com sucesso![/bold green]\n")

            # info = parse_protinfo()
            # partes = "\n".join(
            #     [
            #         f"[green]{p['nome']}[/green]  [cyan]{p['http']}[/cyan]"
            #         for p in info["partes"]
            #     ]
            # )
            # bloco = (
            #     f"[bold]Sessão:[/bold] {info['nome']} ({info['sid']})\n"
            #     f"[bold]Partes:[/bold] {info['numero_partes']} | Threshold: {info['threshold']}\n"
            #     f"[bold]Grupo:[/bold] {info['grupo']}\n"
            #     f"[bold]Provas:[/bold] {info['provas']} | [bold]Hash:[/bold] {info['hash']}\n"
            #     f"[bold]PRG:[/bold] {info['prg']} | [bold]Desafio (RO):[/bold] {info['vbitlenro']} bits\n"
            #     f"[bold]Distância estatística:[/bold] {info['distancia_estatistica']}\n"
            #     f"[bold]Largura dos votos:[/bold] {info['largura_voto']} ({'vetorial' if info['largura_voto'] > 1 else 'padrão'})\n"
            #     f"[bold]Bulletin board:[/bold] {info['bulletin_board'].split('.')[-1]} | [bold]Max ciphertexts:[/bold] {info.get('maxciph', '0')}\n\n"
            #     f"[bold]Mix Servers:[/bold]\n{partes}"
            # )
            # console.print(Panel(bloco, title="Configuração do Protocolo"))
            input("[CONTINUAR]")
            return keygen.show()
        else:
            console.print("\n[bold red]Erro ao executar o setup.[/bold red]\n")
            return False
    else:
        console.print("[italic]Setup cancelado.[/italic]")
        return home.show()
