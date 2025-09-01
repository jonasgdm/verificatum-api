from ui.spinner import run_with_spinner
from services import flask_api, verificatum_api
from app import mock_election
from infra.encryptors.node_daemon import NodeDaemonEncryptor
from infra.encryptors.parallel_encryptor import ParallelEncryptPool
import json
from utils.electionConfig_parser import load_election_config


def show(_=None):
    print("benchmark")
    run_with_spinner(
        lambda: verificatum_api.post_setup(), text="Configurando setup do Guardian..."
    )
    run_with_spinner(lambda: verificatum_api.post_keygen(), "Criando chave pública...")
    config = load_election_config()
    hex_str = verificatum_api.get_publickey()
    key_bytes = bytes.fromhex(hex_str)
    key = json.dumps(list(key_bytes))

    encryptor = ParallelEncryptPool(
        key, script="encryptor/daemon_encrypt.js", pool_size=3, max_workers=4
    )
    app = mock_election.MockElection(key, config, encryptor)

    run_with_spinner(lambda: app.simulate(), "Cifrando Votos...")
    run_with_spinner(
        lambda: flask_api.post_gavt("output/gavt.json"),
        text="Enviando para o backend...",
    )
    run_with_spinner(lambda: flask_api.process_gavt(), text="Processando Votos...")

    run_with_spinner(
        lambda: verificatum_api._post(
            "/shuffler/setup?publicKeyUrl=http://localhost:8080/guardian/public-key"
        ),
        text="Configurando rede de mistura...",
    )
    run_with_spinner(
        lambda: flask_api._post("/shuffle"), text="Enviando Ciphertexts..."
    )
    run_with_spinner(
        lambda: verificatum_api._post("/shuffler/shuffle"), "Executando Shuffle"
    )
    app.export_tally()

    input()
    return "home", None
