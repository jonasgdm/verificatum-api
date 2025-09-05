from rich import print
from rich.console import Console


from services.verificatum_api import post_setup
from utils.protinfo_parser import parse_protinfo


from ui.panel import shell
from ui.prompt import select
from ui.spinner import run_with_spinner

console = Console()


def show(_=None):
    console.clear()

    title = "[bold blue]Passo 1 - Configuração da Rede[/bold blue]"
    txt = """
[white]O setup inicializa a infraestrutura da mixnet, distribuindo e sincronizando a configuração entre os nós.[/white]

[bold]Etapas realizadas:[/bold]
• Criação da sessão criptográfica (ID e nome únicos).
• Geração de arquivos locais para cada nó da mixnet.
• Registro dos endpoints de comunicação (HTTP e Hint).
• Compartilhamento dos arquivos entre todos os nós.
• Fusão dos arquivos de configuração em um único protocolo (protInfo.xml).

Ao final, todos os nós terão uma configuração sincronizada, pronta para executar o protocolo com [bold]threshold[/bold] de decifração.
"""

    console.print(shell(title, txt))

    escolha = select(
        "Deseja iniciar o setup?",
        ["1.Iniciar Setup", "0.Voltar"],
    )

    if escolha.startswith("1"):
        response = run_with_spinner(lambda: post_setup())
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
            title = "Configuração do Protocolo"
            console.print(shell(title, bloco))
            input("[CONTINUAR]")
            return "sim.keygen", None
        else:
            console.print("\n[bold red]Erro ao executar o setup.[/bold red]\n")
            input("> Voltar")
            return "home", None
    else:
        console.print("[italic]Setup cancelado.[/italic]")
        return "sim.sim_menu", None
