import questionary


def select(title: str, choices: list[str]):
    return questionary.select(title, choices=choices).ask()


def text(title: str, validate_int: bool = False, default: str | None = None):
    if validate_int:
        return questionary.text(
            title,
            default=default or "",
            validate=lambda x: x.isdigit() or "Digite um inteiro.",
        ).ask()
    return questionary.text(title, default=default).ask()


def confirm(title: str, default: bool = True):
    return questionary.confirm(title, default=default).ask()
