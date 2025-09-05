ROUTES = {}


def route(screen_name):
    def register(show_screen_fn):
        ROUTES[screen_name] = show_screen_fn
        return show_screen_fn

    return register


def run(start="home"):
    current_screen, payload = start, None
    while current_screen is not None:
        # pega a função correspondente ao nome atual
        show_screen_fn = ROUTES[current_screen]

        # executa a função, passando o payload
        current_screen, payload = show_screen_fn(payload)
