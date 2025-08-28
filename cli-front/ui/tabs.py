from typing import Iterable, Callable
from rich.console import Console

console = Console()


def loop(
    items: Iterable,
    page_size: int = 5,
    render_row: Callable = lambda i, x: console.print(x),
):
    items = list(items)
    n = len(items)
    if n == 0:
        console.print("[yellow]Sem dados.[/yellow]")
        return
    page = 0
    while True:
        start, end = page * page_size, min((page + 1) * page_size, n)
        console.clear()
        console.print(f"[bold]Itens {start+1}-{end} de {n}[/bold]")
        for i, x in enumerate(items[start:end], start=start + 1):
            render_row(i, x)
        cmd = input("\n[Enter]=próx, [p]=ant, [q]=sair: ").strip().lower()
        if cmd == "q":
            break
        if cmd == "p" and page > 0:
            page -= 1
        elif end < n:
            page += 1
