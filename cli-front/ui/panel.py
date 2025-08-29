from rich.panel import Panel
from rich.align import Align

DEFAULT_WIDTH = 90
DEFAULT_BORDER = "cyan"


def shell(
    title: str,
    body: str,
    width: int = DEFAULT_WIDTH,
    border_style: str = DEFAULT_BORDER,
):
    return Panel(
        Align.center(body, vertical="middle"),
        title=f"[bold cyan]{title}[/bold cyan]",
        width=width,
        padding=(1, 4),
        border_style=border_style,
    )


def note(text: str):
    return Panel(text, border_style="grey50")


def error(text: str):
    return Panel(f"[red]{text}[/red]", border_style="red")


def shell_variant_2(
    title: str,
    body: str,
    width: int = DEFAULT_WIDTH,
    border_style: str = DEFAULT_BORDER,
):
    return Panel(
        Align.left(body, vertical="middle"),
        title=f"[bold cyan]{title}[/bold cyan]",
        width=width,
        padding=(1, 4),
        border_style=border_style,
    )
