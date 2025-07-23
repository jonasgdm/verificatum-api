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

GAVT_FILE = "./uploads/output/gavt.json"
OUTPUT_DIR = "./output"


def prf(seed: str, data: str) -> int:
    return int.from_bytes(
        hmac.new(seed.encode(), data.encode(), hashlib.sha256).digest(), "big"
    )


class ShuffleController(MethodView):
    def post(self, index):
        file_path = f"./output/DuplicateVotesTable_{index}"

        if not os.path.exists(file_path):
            return jsonify({"error": f"Arquivo {file_path} não encontrado"}), 404

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "http://localhost:8080/shuffler/receive-ciphertexts",
                    files={"file": (f"DuplicateVotesTable_{index}", f, "text/plain")},
                )

                print(">>>", response)

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

        grouped = defaultdict(list)
        for vote in anyvotes:
            grouped[vote["tokenID"]].append(vote)

        duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
        cargos_removidos = defaultdict(list)

        for tokenID, votos in duplicates.items():
            if len(votos) != 2:
                continue  # tratamento só para pares por enquanto

            v1, v2 = votos
            r1 = prf(seed_duplicate, json.dumps(v1, sort_keys=True))
            r2 = prf(seed_duplicate, json.dumps(v2, sort_keys=True))

            _, removed = (v1, v2) if r1 > r2 else (v2, v1)

            for i, ciphertext in enumerate(removed["encryptedVotes"]):
                cargos_removidos[i].append(ciphertext)

        for idx, ciphertexts in cargos_removidos.items():
            path = os.path.join(OUTPUT_DIR, f"DuplicateVotesTable_{idx}")
            with open(path, "w", encoding="utf-8") as f:
                for c in ciphertexts:
                    f.write(c + "\n")

        return (
            jsonify({"status": "processed", "tokens": len(duplicates)}),
            200,
        )  # sem resposta, só efeito colateral nos arquivos


class GAVTController(MethodView):
    def post(self):
        if "file" not in request.files:
            return jsonify({"erro": "Arquivo não enviado"}), 400
        file = request.files["file"]
        file.save(f"./uploads/{file.filename}")
        return jsonify({"mensagem": "Arquivo recebido com sucesso"}), 200


class ParseController(MethodView):
    def post(self):
        pass


class Cypher01Controller(MethodView):
    def get(self):
        with open("logs/Ciphertexts01Native", "r") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]

        return jsonify(linhas)


class Cypher02Controller(MethodView):
    def get(self):
        with open("logs/Ciphertexts02Native", "r") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]

        return jsonify(linhas)


class AVTMockController(MethodView):

    # {
    #     "nMachines": 1,
    #     "nContestOptions": [
    #         10,
    #         10,
    #         10,
    #         10,
    #         10
    #         ]
    #     "nTotalVotes": 10,
    #     "nAnyVotes": 1
    #     "nDoubleVotes": 1
    # }

    def post(self):
        data = request.get_json()

        n_machines = data.get("nMachines")
        number_contests_options = data.get("nContestOptions")
        n_total_votes = data.get("nTotalVotes")
        n_any_votes = data.get("nAnyVotes")
        n_double_votes = data.get("nDoubleVotes")

        candidate_digits = self.gen_candidates_codes(number_contests_options)
        if len(number_contests_options) == 5:
            number_contests_options = [0, 0] + number_contests_options
        else:
            number_contests_options + [0, 0, 0, 0, 0]
        candidate_digits = self.gen_candidates_codes(number_contests_options)

        gavt = []
        for i in range(n_any_votes):
            vote = self.genAnyVote(self.genTokenID(i), candidate_digits, n_machines)
            gavt.append(vote)

        for _ in range(n_double_votes):
            double_Vote = random.choice(gavt)
            gavt.append(double_Vote)

        conventional = []
        for i in range(n_total_votes - n_any_votes):
            vote = self.genConventionalVote(candidate_digits)
            conventional.append(vote)

        return {"GAVT": gavt, "total": gavt + conventional}

    def genAnyVote(self, tokenid, candidate_codes, nmachines):
        # ELEICOES MUNICIPAIS
        # vereador: 5 digitos
        # prefeito: 2 digitos

        # ELEICOES NACIONAIS
        # dep. federal: 4 digitos
        # dep. estadual: 5 digitos
        # Senador: 3 digitos
        # Gov.: 2 digitos
        # Presidente: 2 digitos
        # [0, 0, 2, 3, 4, 5, 6]

        metadata = {
            "hasbiometry": True,
            "votingMachineID": random.randint(1, nmachines),
        }

        candidates = []
        for codes in candidate_codes:
            choice = random.choice(codes)  # escolher candidato
            candidates.append(choice)
        return {"tokenID": tokenid, "candidates": candidates, "metadata": metadata}

    def gen_candidates_codes(self, n_contest_options):
        candidates_digits = [
            5,
            2,
            4,
            5,
            3,
            2,
            2,
        ]  # vereador, prefeito, dep. fed., est., senador, gov., pres.
        candidate_codes = []
        for i, n in enumerate(n_contest_options):
            if n == 0:
                continue  # pula cargos com 0 candidatos
            digits = candidates_digits[i]
            start = int("9" * digits)

            codes = [start - j for j in range(n)]
            candidate_codes.append(codes)

        return candidate_codes

    def genTokenID(voter_index: int, seed="mock-election-2025"):
        base_string = f"{seed}-{voter_index}"
        return hashlib.sha256(base_string.encode()).hexdigest()[:12]


class Mix1Controller(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.mix(1))


class Mix2Controller(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.mix(2))


class KeysController(MethodView):
    def get(self):
        return jsonify(
            {
                "key1": "MIXNODE1-KEY-ABCDEF123456",
                "key2": "MIXNODE2-KEY-789XYZ987XYZ",
            }
        )


class DecodeController(MethodView):
    def post(self):
        return jsonify({"votos": ["C", "A", "B", "A", "C", "B"]})
