from flask.views import MethodView
from flask import request, jsonify
from services import VerificatumApiService
import time
import string
import random
import hashlib


class SetupController(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.setup())


class KeyGenController(MethodView):
    def get(self):
        return jsonify(VerificatumApiService.get_key())

    def post(self):
        return jsonify(VerificatumApiService.keygen())


class GenerateCyphertextsController(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.cyphertexts())

    def get(self):
        with open("logs/ciphsNative", "r") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]
        return jsonify(linhas)


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


class MixController(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.mix())


class VerifyController(MethodView):
    def post(self):
        return jsonify(VerificatumApiService.verify())


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
