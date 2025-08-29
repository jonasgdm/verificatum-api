# ui/tabs.py
import readchar
from rich.console import Console
from rich.align import Align
from rich.table import Table
from rich import box

console = Console()


def render_tabs_line(tabs, active_idx):
    parts = []
    for i, tab in enumerate(tabs):
        label = f" {tab} "
        if i == active_idx:
            parts.append(f"[reverse][bold]{label}[/bold][/reverse]")
        else:
            parts.append(f"[dim]{label}[/dim]")
    return " ".join(parts)


def tabs_loop(
    data: dict[str, dict[str, int]], title_prefix="Tally", header_style="bold green"
):
    """
    Mostra dados em abas: cada chave de `data` é uma aba (ex.: cargo),
    e o valor é um dicionário {candidato: votos}.
    """
    cargos = list(data.keys())
    if not cargos:
        console.print("[yellow]Nenhum dado encontrado.[/yellow]")
        return

    idx = 0
    while True:
        console.clear()
        console.print(Align.center(render_tabs_line(cargos, idx)))
        console.print()

        cargo = cargos[idx]
        votos = data[cargo]

        table = Table(
            title=f"{title_prefix} - {cargo.upper()}",
            box=box.SIMPLE_HEAVY,
            header_style=header_style,
        )
        table.add_column("Candidato", justify="center")
        table.add_column("Votos", justify="center")
        for cand, count in votos.items():
            table.add_row(str(cand), str(count))

        console.print(table)
        console.print(Align.center("[dim]← → trocar aba  |  q sair[/dim]"))

        key = readchar.readkey()
        if key in (readchar.key.RIGHT, " "):
            idx = (idx + 1) % len(cargos)
        elif key == readchar.key.LEFT:
            idx = (idx - 1) % len(cargos)
        elif key in ("q", "Q", readchar.key.ESC):
            break
