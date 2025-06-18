import json
from services.MockElection import MockElection
import ast
import questionary
from rich.console import Console
import subprocess
from pathlib import Path
import json
from services.MockElection import MockElection
from utils.electionConfig_parser import load_election_config
import os
from rich.spinner import Spinner
from rich.live import Live

console = Console()


def run(cmd, cwd):
    print(f">>> {cmd}")
    input("[continuar]")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def show():
    console.clear()
    choice = questionary.select("", choices=["[MIXAR COM DEMO]", "[SAIR]"]).ask()
    if choice == "[MIXAR COM DEMO]":
        input("EXECUTAR:\n ./clean\n /.info_files\n ./keygen\n[ENTER] para continuar")
        spinner = Spinner("dots", text="Gerando votos e cifrando...")
        with Live(spinner, refresh_per_second=10, transient=True):
            mixnet_dir = Path(__file__).resolve().parent.parent / "mixnet"
            # run("./delete", cwd=mixnet_dir)
            # run("./clean", cwd=mixnet_dir)
            # run("./info_files", cwd=mixnet_dir)
            mydemodir = mixnet_dir / "mydemodir"
            # run("./keygen", cwd=mixnet_dir)
            with open("electionConfig.json", "r") as f:
                conf = json.load(f)
            with open("../cli-front/mixnet/mydemodir/Party01/publicKey", "rb") as f:
                key_bytes = f.read()
                key = json.dumps(list(key_bytes))

            election = MockElection(key, conf)
            election.simulate()
            input_path = "output/gavt.json"
            output_path = mydemodir / "Party01" / "ciphertexts_ext"
            with open(input_path, "r") as f:
                data = json.load(f)

            with open(output_path, "w") as out:
                for entry in data:
                    for enc_vote in entry["encryptedVotes"]:
                        # print(enc_vote + "\n")
                        out.write(enc_vote + "\n")

        # run(
        #     "vmnc -ciphs -sloppy -ini native mydemodir/Party01/protInfo.xml mydemodir/Party01/ciphertexts_ext mydemodir/Party01/ciphertexts",
        #     mixnet_dir,
        # )
        # os.system(
        #     f"cp {mydemodir/ "Party01" / "ciphertexts"} {mydemodir/ "Party02" / "ciphertexts"}"
        # )
        # os.system(
        #     f"cp {mydemodir/ "Party01" / "ciphertexts"} {mydemodir/ "Party02" / "ciphertexts"}"
        # )
        input(
            "EXECUTAR:\n ./ciphs_native_to_raw, ./mix E ./decrypt\n[ENTER] para continuar"
        )
        with open(mydemodir / "Party01" / "plaintexts", "r") as f:
            content = f.read().strip()

        print("📄 Conteúdo de 'plaintexts':")
        print(content)

    # path = "../cli-front/mixnet/mydemodir/Party01/publicKey"
    # path2 = "../cli-front/publicKey"
    # with open(path, "rb") as f:
    #     key_bytes = f.read()
    #     key = list(key_bytes)
    # with open("electionConfig.json", "r") as f:
    #     conf = json.load(f)

    # e = MockElection(key, conf)

    # encoded = e.encrypt("Tesasdfasfdt")
    # # Converter para bytes
    # byte_data = bytes(ast.literal_eval(encoded))

    # # Converter para hexadecimal
    # hex_string = byte_data.hex()
    # print(hex_string)
