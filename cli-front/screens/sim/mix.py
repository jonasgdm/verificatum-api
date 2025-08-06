from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.layout import Layout
from rich.table import Table
from rich.columns import Columns
import questionary

console = Console()


def show():
    titulo = "[bold blue]Etapa 1 – Simular Votação[/bold blue]"

    descricao = (
        "[white]Esta etapa simula o ciclo completo de votação digital com mobilidade,[/white] "
        "desde a preparação da plataforma criptográfica até a emissão e cifra de votos simulados."
        "\n\n[white]O processo é composto pelas seguintes fases:[/white]\n"
        "- [bold]Setup:[/bold] Inicializa a estrutura da mixnet usando o Verificatum.\n"
        "- [bold]Geração de Chave Pública:[/bold] Gera a chave pública da eleição.\n"
        "- [bold]Simulação de Votos:[/bold] Gera votos convencionais, nulos e duplicados no frontend.\n"
        "- [bold]Cifragem:[/bold] Os votos são cifrados com a chave pública gerada.\n"
        "- [bold]Tratamento de Duplicados:[/bold] Votos duplicados são processados no backend.\n"
        "- [bold]Envio ao Verificatum:[/bold] Os votos cifrados (ciphertexts) são enviados para o embaralhamento (mixing)."
    )

    painel_descricao = Panel(
        Align.left(descricao),
        title=titulo,
        border_style="blue",
        padding=(1, 4),
        width=90,
    )

    # Adiciona um "esquemático textual"
    esquema = Table.grid(padding=1)
    esquema.add_column(justify="center")
    esquema.add_row("[bold white]⛓️ Esquema de Comunicação:[/bold white]")
    esquema.add_row("📦 [bold]Verificatum[/bold] → Setup da Mixnet")
    esquema.add_row("🔑 [bold]Verificatum[/bold] → Geração de chave pública")
    esquema.add_row(
        "🧪 [bold]Frontend[/bold] → Simula votos com base em electionConfig.json"
    )
    esquema.add_row("🔐 [bold]Frontend[/bold] → Cifra os votos com a chave pública")
    esquema.add_row("📡 [bold]Backend Flask[/bold] → Processa votos duplicados")
    esquema.add_row(
        "📤 [bold]Backend Flask[/bold] → Envia ciphertexts para Verificatum"
    )

    painel_esquema = Panel(
        Align.center(esquema),
        title="[bold green]Fluxo de Comunicação[/bold green]",
        border_style="green",
        width=90,
        padding=(1, 2),
    )

    console.clear()
    console.print(Columns([painel_descricao, painel_esquema]))

    escolha = questionary.select(
        "Como deseja continuar?",
        choices=[
            "1. Iniciar Etapa de Simulação",
            "0. Voltar ao menu principal",
        ],
    ).ask()

    if escolha.startswith("1"):
        from screens import simulacao_etapas

        simulacao_etapas.show()
    else:
        return
