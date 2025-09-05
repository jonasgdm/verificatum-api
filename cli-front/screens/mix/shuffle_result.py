# screens/shuffle_result.py

import readchar
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.console import Group

from services import verificatum_api, flask_api
from utils import log_parser

from screens.mix import show_ciphertexts

from ui.panel import error

console = Console()


def _tabs_line(tabs, active_idx):
    """
    Desenha as abas no topo. Aba ativa em destaque.
    """
    parts = []
    for i, tab in enumerate(tabs):
        label = f" {tab} "
        if i == active_idx:
            parts.append(f"[reverse][bold]{label}[/bold][/reverse]")
        else:
            parts.append(f"[dim]{label}[/dim]")
    return " ".join(parts)


def render_summary_tables(summary: dict):
    if not summary:
        return "[red]Nenhuma informação encontrada no log do shuffle.[/red]"

    # Tabela de tempos
    t_tempos = Table(title="Tempo Decorrido", header_style="bold cyan")
    t_tempos.add_column("Métrica")
    t_tempos.add_column("ms", justify="right")

    t_tempos.add_row("Execução total", str(summary.get("execution_ms", "-")))
    t_tempos.add_row("Tempo de Rede", str(summary.get("network_ms", "-")))
    t_tempos.add_row("Tempo Ffetivo", str(summary.get("effective_ms", "-")))
    t_tempos.add_row("Tempo de Espera", str(summary.get("idle_ms", "-")))
    t_tempos.add_row("Tempo de Computação", str(summary.get("computation_ms", "-")))

    # Tabela de comunicação
    comm = summary.get("communication", {})
    t_comm = Table(title="Tamanho da Comunicação", header_style="bold cyan")
    t_comm.add_column("Métrica")
    t_comm.add_column("bytes", justify="right")

    t_comm.add_row("Enviado", str(comm.get("sent_bytes", "-")))
    t_comm.add_row("Recebido", str(comm.get("received_bytes", "-")))
    t_comm.add_row("Total", str(comm.get("total_bytes", "-")))

    # Prova
    t_proof = Table(title="Prova", header_style="bold cyan")
    t_proof.add_column("Descrição")
    t_proof.add_column("bytes", justify="right")
    t_proof.add_row("Tamanho da prova", str(summary.get("proof_size_bytes", "-")))

    return Group(t_tempos, t_comm, t_proof)


def show(payload):

    tabs = ["Ciphertexts", "Log"]
    idx = 0  # aba ativa

    log = verificatum_api.get_log()

    summary = log_parser.parse_shuffle_summary(log)

    ciphertextss = flask_api._get("/GAVT")
    shuffled = verificatum_api.get_shuffled()
    if not shuffled:
        console.clear()
        console.print(
            error("Nenhum shuffle encontrado.\nExecute o shuffle antes de visualizar.")
        )
        input("\nPressione Enter para continuar...")
        return "mix.single_shuffle", None

    # os.makedirs("input", exist_ok=True)  # cria a pasta se não existir
    with open("input/not_shuffled.txt", "w") as f:
        f.write(ciphertextss)
    with open("input/shuffled.txt", "w") as f:
        f.write(shuffled)

    page = 0
    PER_PAGE = 10

    while True:
        console.clear()
        console.print(Align.center(_tabs_line(tabs, idx)))
        console.print()

        if tabs[idx] == "Log":
            console.print(render_summary_tables(summary))
        elif tabs[idx] == "Ciphertexts":
            show_ciphertexts.render(
                console, "input/not_shuffled.txt", "input/shuffled.txt", page, PER_PAGE
            )

        console.print(
            Align.center(
                "[dim]← → troca de aba | a anterior | d/esp espaço próxima página | q sair[/dim]"
            )
        )

        key = readchar.readkey()
        if key in (readchar.key.RIGHT, " "):
            idx = (idx + 1) % len(tabs)
        elif key == readchar.key.LEFT:
            idx = (idx - 1) % len(tabs)
        elif key == "a" and page > 0 and tabs[idx] == "Ciphertexts":
            page -= 1
        elif key in ("d", " ") and tabs[idx] == "Ciphertexts":
            page += 1
        elif key in ("q", "Q", readchar.key.ESC):
            return "mix.single_shuffle", None
