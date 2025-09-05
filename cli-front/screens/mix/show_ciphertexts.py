# screens/mix/show_ciphertexts.py

from rich.table import Table
from rich.align import Align
from rich import box
from rich.panel import Panel

PREFIX = "00000000020000000002010000002100"


def _read_lines(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def _abbrev(s: str, n=50):
    if s.startswith(PREFIX):
        s = "…" + s[len(PREFIX) :]
    return s if len(s) <= n else s[:n] + "…"


def render(console, orig_path: str, shuf_path: str, page: int, per_page: int):
    orig_list = _read_lines(orig_path)
    shuf_list = _read_lines(shuf_path)
    n = min(len(orig_list), len(shuf_list))

    start = page * per_page
    end = min(start + per_page, n)
    # Texto explicativo
    explanation = (
        "[white]\n"
        "• Cada ciphertext da coluna [cyan]Antes[/cyan] corresponde a um voto cifrado na ordem original.\n\n"
        "• A mixnet aplica uma [bold]permutação criptograficamente verificada[/bold], embaralhando toda a lista.\n\n"
        "• Durante o shuffle ocorre [bold]re-encriptação[/bold]: cada ciphertext muda de forma,\n"
        "   mas continua matematicamente equivalente ao original.\n\n"
        "• Uma prova de correção ([italic]zero-knowledge proof[/italic]) atesta que a saída é\n"
        "   apenas uma permutação re-encriptada da entrada.\n\n"
        "• Isso preserva [bold green]integridade[/bold green] e [bold magenta]anonimato[/bold magenta],\n"
        "   impossibilitando ligar posições iniciais às finais.\n\n"
        "[/white]"
    )
    panel = Panel(
        explanation,
        title="[bold blue]O Shuffle[/bold blue]",
        width=100,
    )
    console.print(panel)
    table = Table(
        title=f"Ciphertexts [ {start+1} – {end} de {n} ]",
        box=box.SIMPLE_HEAVY,
        header_style="bold cyan",
    )
    table.add_column("Idx", justify="right", width=6)
    table.add_column("Antes de misturar")
    table.add_column("Depois de misturar")

    for i in range(start, end):
        table.add_row(str(i + 1), _abbrev(orig_list[i]), _abbrev(shuf_list[i]))

    console.print(Align.center("[bold]Ciphertexts (Antes → Depois)[/bold]"))
    console.print()
    console.print(table)
