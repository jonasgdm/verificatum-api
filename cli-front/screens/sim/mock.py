import json
from rich import print
from rich.console import Console

from services import flask_api
from services.verificatum_api import get_publickey
from utils.electionConfig_parser import load_election_config
from app.mock_election import MockElection
from infra.encryptors.node_daemon import NodeDaemonEncryptor

from ui.panel import shell
from ui.prompt import input_text, select
from ui.spinner import run_with_spinner
from ui.table import simple


CONFIG_PATH = "electionConfig.json"
console = Console()


def update_config(any_votes, double_votes):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    config["anyVotes"] = any_votes
    config["doubleVotes"] = double_votes

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def vote_params():
    any_votes = input_text(
        "Quantos AnyVotes deseja gerar?",
        validate_int=lambda val: val.isdigit() and int(val) >= 0,
        default="10",
    )

    double_votes = input_text(
        "Quantos votos duplicados deseja gerar?",
        validate_int=lambda val: val.isdigit()
        and int(val) >= 0
        and int(val) <= int(any_votes),
        default="5",
    )

    return int(any_votes), int(double_votes)


def format_config(config):
    base = (
        f"[bold]Votos totais:[/bold] {config['anyVotes'] + config['doubleVotes'] + config['conventionalVotes']}\n"
        f"[bold]Any Votes:[/bold] {config['anyVotes']}\n"
        f"[bold]Votos Duplicados:[/bold] {config['doubleVotes']}\n"
        f"[bold]Votos Convencionais:[/bold] {config['conventionalVotes']}\n"
    )

    return base


def table_cargos(cargos):
    rows = [
        (cargo["contest"].capitalize(), cargo["candidates"])
        for cargo in cargos
        if cargo["candidates"] != 0
    ]
    simple(
        headers=["[magenta]Cargo[/magenta]", "[magenta]Nº de Candidatos[/magenta]"],
        rows=rows,
        title="Cargos Ativos",
    )


def show(_=None):

    while True:
        console.clear()
        config = load_election_config()

        if not config:
            console.print(
                "[bold red]Arquivo electionConfig.json não encontrado![/bold red]"
            )
            input("Voltando... ")
            return "home", None

        title = "[bold blue]Passo 3 - Simução de Votos[/bold blue]"
        txt = """
[white]
Esta etapa gera votos simulados que são cifrados com a chave pública da mixnet. Após a geração, os votos são processados para remover duplicações. Apenas a parte cifrada (escolhas por cargo) é enviada à mixnet para o embaralhamento.
[/white]

[blue]Geração e Cifragem → Remoção de Duplicados → Envio à Mixnet[/blue]

Configure os parâmetros em [bold]electionConfig.json[/bold]
"""

        console.print(shell(title, txt))

        any_votes, double_votes = vote_params()
        update_config(any_votes, double_votes)
        config = load_election_config()

        console.print(shell("Configuração da Eleição", format_config(config), width=20))
        console.print(table_cargos(config["options"]))

        escolha = select(
            "Deseja gerar os votos simulados?",
            ["1. Gerar Votos", "2. electionConfig.json", "[↩ VOLTAR]"],
        )

        if escolha.startswith("1"):
            run_with_spinner(
                lambda: run_mock(config), text="Gerando votos simulados..."
            )

            input("[Continuar]")

            run_with_spinner(
                lambda: flask_api.post_gavt("output/gavt.json"),
                text="Enviando para o backend...",
            )
            run_with_spinner(
                lambda: flask_api.process_gavt(), text="Processando Votos..."
            )

            return "sim.result", None
        elif escolha.startswith("2"):
            continue
        else:
            console.print("[italic]Operação cancelada.[/italic]")
            input("Voltando...")
            return "home", None


def run_mock(config):
    hex_str = get_publickey()
    key_bytes = bytes.fromhex(hex_str)
    key = json.dumps(list(key_bytes))

    encryptor = NodeDaemonEncryptor(key)
    app = MockElection(key, config, encryptor)
    app.simulate()

    app.export_tally()
    try:
        encryptor.close()
    except Exception:
        pass
