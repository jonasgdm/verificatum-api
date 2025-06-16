import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEMO_DIR = BASE_DIR / "verificatum-demo"


def load_file(filename):
    caminho = BASE_DIR / DEMO_DIR / filename
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8")


def parse_protinfo(filename="01/protInfo.xml"):
    """
    Lê e extrai as informações principais do protinfo.xml
    Retorna um dicionário estruturado com metadados e participantes.
    """
    raw = load_file(filename)
    root = ET.fromstring(raw)

    protocolo = {
        "versao": root.findtext("version"),
        "sid": root.findtext("sid"),
        "nome": root.findtext("name"),
        "descricao": root.findtext("descr"),
        "numero_partes": int(root.findtext("nopart")),
        "threshold": int(root.findtext("thres")),
        "grupo": root.findtext("pgroup"),
        "bulletin_board": root.findtext("bullboard"),
        "provas": root.findtext("corr"),
        "hash": root.findtext("rohash"),
        "prg": root.findtext("prg"),
        "vbitlen": int(root.findtext("vbitlen")),
        "vbitlenro": int(root.findtext("vbitlenro")),
        "ebitlen": int(root.findtext("ebitlen")),
        "ebitlenro": int(root.findtext("ebitlenro")),
        "largura_voto": int(root.findtext("width")),
        "distancia_estatistica": int(root.findtext("statdist")),
        "partes": [],
    }

    for p in root.findall("party"):
        protocolo["partes"].append(
            {
                "nome": p.findtext("name"),
                "http": p.findtext("http"),
                "hint": p.findtext("hint"),
                "pkey": p.findtext("pkey")[:64] + "...",
            }
        )

    return protocolo
