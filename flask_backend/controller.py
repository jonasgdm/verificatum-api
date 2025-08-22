from flask.views import MethodView
from flask import request, jsonify
from services.publicKey_service import VerificatumApiService
from services.vote_processing_services import process_gavt
import time
import string
import random
import requests
import hashlib
import os, json, hmac, hashlib
from collections import defaultdict

GAVT_FILE = "./uploads/gavt.json"
OUTPUT_DIR = "./output"


def prf(seed: str, data: str) -> int:
    return int.from_bytes(
        hmac.new(seed.encode(), data.encode(), hashlib.sha256).digest(), "big"
    )


class ShuffleController(MethodView):
    def post(self):
        file_path = f"./output/DuplicateVotesTable"

        if not os.path.exists(file_path):
            return jsonify({"error": f"Arquivo {file_path} não encontrado"}), 404

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "http://localhost:8080/shuffler/receive-ciphertexts",
                    files={"file": (f"DuplicateVotesTable", f, "text/plain")},
                )

            if response.ok:
                return jsonify(response.json()), 200
            else:
                return (
                    jsonify(
                        {
                            "error": "Erro no Verificatum",
                            "status_code": response.status_code,
                            "body": response.text,
                        }
                    ),
                    500,
                )

        except Exception as e:
            return jsonify({"error": str(e)}), 500


class PublicKeyController(MethodView):
    def get(self):
        return jsonify(VerificatumApiService.get_key())


class ProcessGAVTController(MethodView):
    def post(self):

        seed_duplicate = "seed_contribuida_por_observadores"

        try:
            with open(GAVT_FILE, "r", encoding="utf-8") as f:
                anyvotes = json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao ler o arquivo GAVT: {e}")
            return "", 204

        # Agrupa votos pelo tokenID
        grouped = defaultdict(list)
        for vote in anyvotes:
            grouped[vote["tokenID"]].append(vote)

        # Filtra tokens com mais de 1 voto
        duplicates = {k: v for k, v in grouped.items() if len(v) > 1}

        votos_removidos = []

        for tokenID, votos in duplicates.items():
            # Escolhe o voto válido (maior PRF)
            melhor_voto = max(
                votos, key=lambda v: prf(seed_duplicate, json.dumps(v, sort_keys=True))
            )

            # Todos os outros são descartados
            for voto in votos:
                if voto is not melhor_voto:
                    votos_removidos.extend(voto["encryptedVotes"])

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Salva todos os votos descartados em um único arquivo
        path = os.path.join(OUTPUT_DIR, "DuplicateVotesTable")
        with open(path, "w", encoding="utf-8") as f:
            for c in votos_removidos:
                f.write(c + "\n")

        return jsonify({"status": "processed", "tokens": len(duplicates)}), 200


class GAVTController(MethodView):
    def post(self):
        if "file" not in request.files:
            return jsonify({"erro": "Arquivo não enviado"}), 400

        file = request.files["file"]

        # garante que a pasta /uploads existe
        os.makedirs("./uploads", exist_ok=True)

        # salva sempre com nome fixo
        filepath = os.path.join("./uploads", "gavt.json")
        file.save(filepath)

        return jsonify({"mensagem": f"Arquivo salvo em {filepath}"}), 200
