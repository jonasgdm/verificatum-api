from flask.views import MethodView
from flask import request, jsonify
from services import VerificatumApiService
import time
import string
import random


class MockController(MethodView):
    def post(self):
        data = request.get_json()
        candidatos = data.get("candidatos")
        votos = data.get("votos")
        duplicatas = data.get("duplicatas")
        # Gerar votos únicos com tokens 1..votos e votos A..(candidatos)
        letras = string.ascii_uppercase[:candidatos]

        votos_unicos = []
        for i in range(1, votos - duplicatas + 1):
            voto = {"token": str(i), "voto": random.choice(letras)}
            votos_unicos.append(voto)

        # Duplicatas são cópias com o mesmo token, mas voto diferente
        votos_mock = votos_unicos.copy()
        votos_duplos = []
        for _ in range(duplicatas):
            base = random.choice(votos_unicos)
            voto_duplo = {"token": base["token"], "voto": random.choice(letras)}
            votos_duplos.append(voto_duplo)
            votos_mock.append(voto_duplo)

        votos = [v["voto"] for v in votos_duplos]
        votos_cifrados = VerificatumApiService.cypher(votos)

        return jsonify(
            {
                "total": len(votos_mock),
                "votos": votos_mock,
            }
        )


class CypherTextController(MethodView):
    def get(self):

        return jsonify(VerificatumApiService.cyphertexts())


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
