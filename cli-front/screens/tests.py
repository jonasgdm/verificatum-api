import json
from app.mock_election import MockElection
from infra.encryptors.node_daemon import NodeDaemonEncryptor


def show():
    with open("electionConfig.json") as f:
        cfg = json.load(f)
    # with open("protinfo/publicKey.json") as f:
    #     pk = f.read()

    encryptor = NodeDaemonEncryptor(pk)  # hoje: daemon local
    app = MockElection(pk, cfg, encryptor)  # domínio recebe a porta
    app.simulate()
    app.export_tally()
    try:
        encryptor.close()
    except Exception:
        pass
