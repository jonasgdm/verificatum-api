import os, json
from rich.console import Console
from ui.tabs import tabs_loop

console = Console()


def show_preliminar_tabs(path="output/tally.json"):
    if not os.path.exists(path):
        console.print(f"[bold red]Arquivo {path} não encontrado.[/bold red]")
        return

    with open(path, "r") as f:
        preliminar = json.load(f)

    # chama o componente de abas
    tabs_loop(
        preliminar,
        title_prefix="Tally Preliminar (INCLUI DoubleVotes)",
        header_style="bold yellow",
    )
