# ui/components/config_summary.py
from ui.panel import shell_variant_2
from utils.electionConfig_parser import load_election_config


def build_config_panel():
    cfg = load_election_config()
    if not cfg:
        return shell("Resumo da Configuração", "[red]Configuração não encontrada[/red]")

    any_votes = int(cfg.get("anyVotes", 0))
    dup_votes = int(cfg.get("doubleVotes", 0))
    conv_votes = int(cfg.get("conventionalVotes", 0))
    total = any_votes + dup_votes + conv_votes
    ativos = len([o for o in cfg.get("options", []) if o.get("candidates", 0) > 0])

    body = (
        f"[bold]Eleições Ativas:[/bold] {ativos}\n\n"
        f"[bold]Total de votos:[/bold] {total}\n"
        f"[bold]AnyVotes:[/bold] {any_votes}\n"
        f"[bold]Duplicados:[/bold] {dup_votes}\n"
        f"[bold]Convencionais:[/bold] {conv_votes}"
    )
    return shell_variant_2("Resumo da Configuração", body)
