# screens/mock.py

import os
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.align import Align

import questionary
import json

# from utils.protinfo_parser import load_file

from services import flask_api
from services.verificatum_api import get_publickey

from screens.mix import shuffle_setup
from screens.sim import result

# from services.mock_vote_service import (
#     generate_mock_votes,
# )  # serviço que você irá implementar
from utils.electionConfig_parser import load_election_config

from app.mock_election import MockElection
from infra.encryptors.node_daemon import NodeDaemonEncryptor

CONFIG_PATH = "electionConfig.json"
console = Console()


def update_config(any_votes, double_votes):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    config["anyVotes"] = any_votes
    config["doubleVotes"] = double_votes
    # config["type"] = type

    # if type == "Municipal":
    #     for cargo in config.get("options", []):
    #         if cargo["contest"] not in ["vereador", "prefeito"]:
    #             cargo["candidates"] = 0
    # else:  # Tipo "Geral"
    #     for cargo in config.get("options", []):
    #         if cargo["contest"] in ["vereador", "prefeito"]:
    #             cargo["candidates"] = 0
    #         else:
    #             cargo["candidates"] = 2

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def vote_params():
    any_votes = questionary.text(
        "Quantos AnyVotes deseja gerar?",
        default="10",
        validate=lambda val: val.isdigit() and int(val) >= 0,
    ).ask()

    double_votes = questionary.text(
        "Quantos votos duplicados deseja gerar?",
        default="5",
        validate=lambda val: val.isdigit() and int(val) >= 0,
    ).ask()

    # tipo = questionary.select(
    #     "Escolha o tipo de eleição:", choices=["Municipal", "Geral"]
    # ).ask()
    return int(any_votes), int(double_votes)


def format_config(config):
    base = (
        f"[bold]Tipo de Eleição:[/bold] {config['type']}\n"
        f"[bold]Votos totais:[/bold] {config['anyVotes'] + config['doubleVotes'] + config['conventionalVotes']}\n"
        f"[bold]Any Votes:[/bold] {config['anyVotes']} | "
        f"[bold]Votos Convencionais:[/bold] {config['conventionalVotes']} | "
        f"[bold]Votos Duplicados:[/bold] {config['doubleVotes']} \n"
        f"[bold]Votos Nulos:[/bold] {config['nullVotes']} | "
        f"[bold]Votos Branco:[/bold] {config['blankVotes']} \n"
    )
    return base


def table_cargos(cargos):
    table = Table(title="Cargos Ativos", show_header=True, header_style="bold magenta")
    table.add_column("Cargo")
    table.add_column("Nº de Candidatos", justify="center")
    for cargo in cargos:
        if cargo["candidates"] != 0:
            table.add_row(cargo["contest"].capitalize(), str(cargo["candidates"]))
    return table


# import questionary

# config = {
#     "anyVotes": 10,
#     "doubleVotes": 5,
#     "blankVotes": 2,
#     "nullVotes": 1,
# }


def show():

    while True:
        console.clear()
        config = load_election_config()

        if not config:
            console.print(
                "[bold red]Arquivo electionConfig.json não encontrado![/bold red]"
            )

        painel_explicacao = Panel(
            Align.left(
                """
[white]
Esta etapa gera votos simulados que são cifrados com a chave pública da mixnet. Após a geração, os votos são processados para remover duplicações. Apenas a parte cifrada (escolhas por cargo) é enviada à mixnet para o embaralhamento.
[/white]

[blue]Geração e Cifragem → Remoção de Duplicados → Envio à Mixnet[/blue]

Configure os parâmetros em [bold]electionConfig.json[/bold]
"""
            ),
            title="[bold blue]Passo 3 - Simução de Votos[/bold blue]",
            border_style="blue",
            width=100,
            padding=(1, 2),
        )
        console.print(painel_explicacao)

        any_votes, double_votes = vote_params()
        update_config(any_votes, double_votes)
        config = load_election_config()

        console.print(
            Panel(format_config(config), title="Configuração da Eleição"), width=80
        )
        console.print(table_cargos(config["options"]))

        escolha = questionary.select(
            "Deseja gerar os votos simulados?",
            choices=["[GERAR VOTOS]", "[RECARREGAR electionConfig.json]", "[↩ VOLTAR]"],
        ).ask()

        if escolha == "[GERAR VOTOS]":
            spinner = Spinner("dots", text="Gerando votos simulados...")
            with Live(spinner, refresh_per_second=10, transient=True):
                hex_str = get_publickey()
                key_bytes = bytes.fromhex(hex_str)
                key = json.dumps(list(key_bytes))  # mesmo formato que você já usava
                encryptor = NodeDaemonEncryptor(key)
                app = MockElection(key, config, encryptor)
                app.simulate()
                app.export_tally()
                try:
                    encryptor.close()
                except Exception:
                    pass

            spinner = Spinner("dots", text="Enviando para o backend...")
            with Live(spinner, refresh_per_second=10, transient=True):
                flask_api.post_gavt("output/gavt.json")

            spinner = Spinner("dots", text="Processando Votos...")
            with Live(spinner, refresh_per_second=10, transient=True):
                flask_api.process_gavt()

            return result.show()
        elif escolha == "[RECARREGAR electionConfig.json]":
            continue
        else:
            console.print("[italic]Operação cancelada.[/italic]")
            return home.show()
