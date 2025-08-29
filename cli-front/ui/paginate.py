# ui/paginate.py
from typing import Callable, Iterable
from rich.console import Console
from rich.table import Table
import readchar

console = Console()


def paginate_table(
    headers: list[str],
    rows: list[list[str]],
    title_fn: Callable[[int, int, int], str] | None = None,
    page_size: int = 5,
    highlight_fn: (
        Callable[[int], str | None] | None
    ) = None,  # recebe índice global, retorna estilo ou None
):
    """Mostra uma tabela paginada: [a]=anter., [d]=próx., [Enter]=sair"""
    n = len(rows)
    if n == 0:
        console.print("[yellow]Sem dados.[/yellow]")
        readchar.readkey()
        return

    page = 0
    while True:
        start = page * page_size
        end = min(start + page_size, n)

        # monta tabela da página
        table = Table(
            title=title_fn(start + 1, end, n) if title_fn else "",
            show_header=True,
            header_style="bold cyan",
        )
        for idx, h in enumerate(headers):
            table.add_column(h, justify="center" if idx > 0 else "left")

        for i in range(start, end):
            style = highlight_fn(i) if highlight_fn else None
            table.add_row(*[str(x) for x in rows[i]], style=style)

        console.clear()
        console.print(table)
        console.print("[dim][a] Anterior  |  [d] Próxima  |  [ENTER] Sair[/dim]")

        k = readchar.readkey()
        if k in ("\r", "\n"):  # Enter
            break
        elif k == "d":
            if end < n:
                page += 1
            else:
                page = 0  # loop pro começo
        elif k == "a":
            if page > 0:
                page -= 1
            else:
                # volta pro fim alinhado ao tamanho da página
                last_full = (n - 1) // page_size
                page = max(0, last_full)
