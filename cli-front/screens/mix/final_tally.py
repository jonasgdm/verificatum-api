# final_tally.py
import os
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

try:
    import readchar  # pip install readchar
except ImportError:
    raise SystemExit("Instale a dependência: pip install readchar")

console = Console()
DIGITS_POR_CARGO = {
    "01": 5,  # prefeito
    "02": 5,  # vereador
    "03": 5,  # dep estadual
    "05": 5,  # dep federal
    "06": 3,  # governador
    "07": 3,  # senador
    "11": 2,  # presidente
}
# mapeamento fixo de cargos (exemplo)
CARGO_IDS = {
    "prefeito": "01",
    "vereador": "02",
    "deputado_estadual": "03",
    "deputado_federal": "05",
    "senador": "06",
    "governador": "07",
    "presidente": "11",
}
INV_CARGO_IDS = {v: k for k, v in CARGO_IDS.items()}

DECRYPT_PATH = os.path.join("decrypted", "decrypted.native")


def _parse_plaintext_line(line: str):
    s = line.strip()
    if len(s) < 7 or not s.isdigit():
        return None
    id_eleicao = s[:4]
    cod_cargo = s[4:6]
    numero_candidato = s[6:]
    return id_eleicao, cod_cargo, numero_candidato


def _contar_descartados_por_cargo(decrypted_lines):
    por_cargo = defaultdict(Counter)
    for ln in decrypted_lines:
        parsed = _parse_plaintext_line(ln)
        if not parsed:
            continue
        _, cod_cargo, numero = parsed
        cod_cargo = str(cod_cargo).zfill(2)
        # Mantém exatamente como veio do plaintext
        por_cargo[cod_cargo][numero] += 1
    return por_cargo


def _tally_original_por_cargo(tally_json):
    resultado = {}
    for cargo_nome, mapa in tally_json.items():
        cod = CARGO_IDS.get(cargo_nome, None)
        if cod is None:
            continue
        # Mantém como string exatamente como veio no JSON
        resultado[cod] = {str(k): int(v) for k, v in mapa.items()}
    return resultado


def _tabs_line(codigos, active_idx):
    """
    Desenha as 'abas' no topo. Aba ativa em destaque.
    """
    parts = []
    for i, cod in enumerate(codigos):
        nome = INV_CARGO_IDS.get(cod, f"Cargo {cod}")
        label = f" {nome} "
        if i == active_idx:
            parts.append(f"[reverse][bold]{label}[/bold][/reverse]")
        else:
            parts.append(f"[dim]{label}[/dim]")
    return " ".join(parts)


def _mostrar_tabela_cargo(cargo_nome, tally_orig_map, tally_desc_map):
    """
    Tabela: Candidato | Original | Descartados | Válidos
    """
    table = Table(title=f"Tally Comparativo - {cargo_nome}", show_lines=True)
    table.add_column("Candidato", justify="center")
    table.add_column("Original", justify="center")
    table.add_column("Descartados", justify="center")
    table.add_column("Válidos", justify="center")

    candidatos = set(tally_orig_map.keys()) | set(tally_desc_map.keys())
    for cand in sorted(candidatos, key=lambda x: (len(x), x)):
        orig = tally_orig_map.get(cand, 0)
        desc = tally_desc_map.get(cand, 0)
        validos = orig - desc
        table.add_row(cand, str(orig), str(desc), str(validos))

    total_original = sum(tally_orig_map.values())
    total_desc = sum(tally_desc_map.values())
    total_validos = total_original - total_desc

    console.print(table)
    console.print(f"[bold]Total original:[/bold] {total_original}")
    console.print(f"[bold]Descartados:[/bold] {total_desc}")
    console.print(f"[bold green]Válidos:[/bold green] {total_validos}\n")


def _mostrar_resumo_global(orig_por_cargo, desc_por_cargo):
    total_orig_global = sum(sum(mapa.values()) for mapa in orig_por_cargo.values())
    total_desc_global = sum(sum(cnt.values()) for cnt in desc_por_cargo.values())
    total_validos_global = total_orig_global - total_desc_global
    console.print(
        Panel(
            f"[bold]Totais (todas as eleições)[/bold]\n"
            f"Original: {total_orig_global}\n"
            f"Descartados: {total_desc_global}\n"
            f"[bold green]Válidos: {total_validos_global}[/bold green]",
            title="Resumo Global",
            width=80,
        )
    )


def mostrar_apuracao_final(tally_json):
    """
    Tela de apuração com 'abas' navegáveis:
      ← →  : troca de aba
      espaço: próxima aba
      G    : resumo global
      Q    : sair
    """
    print(tally_json)
    if not os.path.exists(DECRYPT_PATH):
        console.print(
            "[bold red]Arquivo não encontrado:[/bold red] 'decrypted/decrypted.native'"
        )
        return

    # 1) Ler plaintexts
    with open(DECRYPT_PATH, "r", encoding="utf-8") as f:
        decrypted_votes = [ln.strip() for ln in f if ln.strip()]

    # 2) Contagens
    desc_por_cargo = _contar_descartados_por_cargo(decrypted_votes)
    orig_por_cargo = _tally_original_por_cargo(tally_json)

    # 3) Universo de abas (ordem por codCargo)
    cods = sorted(set(orig_por_cargo.keys()) | set(desc_por_cargo.keys()))
    if not cods:
        console.print("[yellow]Não há cargos para mostrar.[/yellow]")
        return

    idx = 0  # aba ativa

    while True:
        console.clear()

        console.print(
            Panel(
                "[white]\n"
                "• Esta tela mostra a [bold]apuração final[/bold] após a remoção de votos duplicados.\n"
                "• Antes, a mixnet embaralhou e re-encriptou todos os votos para "
                "quebrar a ligação entre eleitor e ciphertext.\n"
                "• Em seguida, votos com o mesmo identificador ([cyan]tokenID[/cyan]) "
                "foram detectados como duplicados.\n"
                "• Em uma eleição real, isso corresponde a tentativas de um mesmo eleitor votar mais de uma vez.\n"
                "• O sistema escolhe um voto válido e [bold red]descarta[/bold red] os demais, "
                "mantendo apenas um voto por eleitor.\n"
                "• O resultado garante [bold green]integridade[/bold green], "
                "[bold green]equidade[/bold green] e [bold magenta]anonimato[/bold magenta].\n"
                "[/white]",
                title="[bold blue]Apuração Final após Descarte de Duplicados[/bold blue]",
                width=100,
                padding=(1, 2),
            )
        )
        console.print(
            Panel(
                "[bold]Apuração Final[/bold]\n"
                "Votos duplicatods foram subtraídos do tally inicial.\n"
                "Use ← → ou espaço para navegar entre eleições. [bold]G[/bold] resumo global, [bold]Q[/bold] sair.",
                title="Resultado Ajustado Após Subtração",
                width=80,
            )
        )

        # Abas
        console.print(Align.center(_tabs_line(cods, idx)))
        console.print()  # linha em branco

        # Tabela da aba ativa
        cod_atual = cods[idx]
        cargo_nome = INV_CARGO_IDS.get(cod_atual, f"Cargo {cod_atual}")
        tally_orig = orig_por_cargo.get(cod_atual, {})
        tally_desc = desc_por_cargo.get(cod_atual, Counter())
        _mostrar_tabela_cargo(cargo_nome, tally_orig, tally_desc)

        # Rodapé de ajuda
        console.print(
            Align.center(
                "[dim]← → / espaço: navegar  |  G: resumo global  |  Q: sair[/dim]"
            )
        )

        # Leitura de tecla
        key = readchar.readkey()
        if key in (readchar.key.RIGHT, " "):
            idx = (idx + 1) % len(cods)
        elif key == readchar.key.LEFT:
            idx = (idx - 1) % len(cods)
        elif key in ("g", "G"):
            console.clear()
            _mostrar_resumo_global(orig_por_cargo, desc_por_cargo)
            console.print("\n[dim]Pressione qualquer tecla para voltar...[/dim]")
            readchar.readkey()
        elif key in ("q", "Q", readchar.key.ESC):
            break
