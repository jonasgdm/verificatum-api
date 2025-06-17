from screens import setup, keygen, mock, mix


def main():
    if setup.show() is False:
        interrupt()
        return
    if keygen.show() is False:
        interrupt()
        return
    if mock.show() is False:
        interrupt()
        return


# mock.show()


def interrupt():
    print("[bold red]Processo interrompido pelo usuário.[/bold red]")


if __name__ == "__main__":
    main()
