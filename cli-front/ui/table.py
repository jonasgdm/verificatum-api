from rich.table import Table
from rich.console import Console

console = Console()


def simple(headers: list[str], rows: list[tuple], title: str | None = None):
    t = Table(title=title or "", show_lines=False, header_style="bold")
    for h in headers:
        t.add_column(h)
    for r in rows:
        t.add_row(*[str(x) for x in r])
    console.print(t)
