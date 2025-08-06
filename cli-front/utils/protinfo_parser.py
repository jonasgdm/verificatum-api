import xml.etree.ElementTree as ET


def parse_protinfo(filename="protinfo"):
    """
    Lê e extrai as informações principais do protinfo.xml
    Retorna um dicionário estruturado com metadados e participantes.
    """
    root = ET.parse(filename)

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
