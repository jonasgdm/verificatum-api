from rich.panel import Panel
from rich.align import Align

DEFAULT_WIDTH = 90
DEFAULT_BORDER = "cyan"


def shell(title: str, body: str, width: int = DEFAULT_WIDTH):
    txt = f"[bold cyan]{title}[/bold cyan]\n\n{body}"
    return Panel(
        Align.center(txt, vertical="middle"),
        width=width,
        padding=(1, 4),
        border_style=DEFAULT_BORDER,
    )


def note(text: str):
    return Panel(text, border_style="grey50")


def error(text: str):
    return Panel(f"[red]{text}[/red]", border_style="red")
