import os, json


def _tabs_line(tabs, active_idx):
    parts = []
    for i, tab in enumerate(tabs):
        label = f" {tab} "
        if i == active_idx:
            parts.append(f"[reverse][bold]{label}[/bold][/reverse]")
        else:
            parts.append(f"[dim]{label}[/dim]")
    return " ".join(parts)


def show_tally_tabs(path="output/tally.json"):
    if not os.path.exists(path):
        console.print(f"[bold red]Arquivo {path} não encontrado.[/bold red]")
        return

    with open(path, "r") as f:
        tally = json.load(f)

    cargos = list(tally.keys())
    if not cargos:
        console.print("[yellow]Nenhuma eleição encontrada no tally.[/yellow]")
        return

    idx = 0
    while True:
        console.clear()
        console.print(Align.center(_tabs_line(cargos, idx)))
        console.print()

        cargo = cargos[idx]
        votos = tally[cargo]

        table = Table(
            title=f"Tally - {cargo.upper()}",
            box=box.SIMPLE_HEAVY,
            header_style="bold green",
        )
        table.add_column("Candidato", justify="center")
        table.add_column("Votos", justify="center")
        for candidato, count in votos.items():
            table.add_row(str(candidato), str(count))

        console.print(table)
        console.print(Align.center("[dim]← → trocar eleição  |  q sair[/dim]"))

        key = readchar.readkey()
        if key in (readchar.key.RIGHT, " "):
            idx = (idx + 1) % len(cargos)
        elif key == readchar.key.LEFT:
            idx = (idx - 1) % len(cargos)
        elif key in ("q", "Q", readchar.key.ESC):
            break
