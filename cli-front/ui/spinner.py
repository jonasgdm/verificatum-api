from rich.spinner import Spinner
from rich.live import Live


def run_with_spinner(task_fn, text="Processando...", spinner="dots", refresh=10):
    """
    Executa task_fn() mostrando um spinner.
    Retorna o valor que a função devolver.
    """
    with Live(Spinner(spinner, text=text), refresh_per_second=refresh):
        return task_fn()
