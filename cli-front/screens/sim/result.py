from rich.console import Console
from ui.panel import shell
from ui.prompt import select
from app.mock_election import MockElection

from screens.sim.result_screens import show_preliminar_tally, show_ciphertexts

console = Console()


def show(_=None):
    while True:
        console.clear()
        title = "[bold blue]Fim da Simulação de Eleição[/bold blue]"
        txt = """
[white]A eleição simulada foi concluída com sucesso. Votos foram gerados, cifrados com a chave pública da mixnet e processados para remover duplicatas.[/white]

[bold]Visualização:[/bold] É possível inspecionar os votos cifrados e o resultado parcial (tally) obtido diretamente dos dados simulados.

[blue]A próxima etapa simularia um ambiente de mixagem,[/blue] com foco em embaralhamento (mixing) e decifração segura usando os servidores da mixnet.
"""

        console.print(shell(title, txt))
        escolha = select(
            "Selecione uma ação:",
            [
                "1.Visualizar Tally Preliminar (inclui votos duplicados)",
                "2.Visualizar Tabela de Votos",
                "↩ Voltar",
            ],
        )

        if escolha.startswith("1"):
            show_preliminar_tally.show_preliminar_tabs()

        elif escolha.startswith("2"):
            show_ciphertexts.paginar_votos()

        else:
            return "home", None
