from screens import home, setup, keygen, mock, mix, mix_demo


def main():
    # screens = [home.show, setup.show, keygen.show, mock.show, mix_demo.show]
    screens = [mix_demo.show]
    for screen in screens:
        if not screen():
            break


def interrupt():
    print("[bold red]Processo interrompido pelo usuário.[/bold red]")


if __name__ == "__main__":
    main()
