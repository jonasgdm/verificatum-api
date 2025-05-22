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


class KeyGenController(MethodView):
    def get(self):
        return jsonify(
            {
                "key": """MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwU6h1RHQlULPfr7FEZ6L
9VV5FdxtEVxHX0uCmkZhAfvNzqT+dC4M0ZLHVcplMfThn3gS2v7UyMqv7K3Tjb8T
yCzhX8cpS/pJfB7M8gTgz7HbYyaZp3zZaX2cwRZ8aD8zKYj2MWRbq3XY+o2VScMg
0vv09U42SK1wMB8I8Zy3nUO8Jz5s8qbJpAxGn+5oX7H2MHrR4Ymh2kMCsPtU1DgZ
OmkMGMKZulr6Yo6+MFev1cb9MB1kZ4VufC0cYlv10xW7tz7ya9x1V8lSn5pTLDeD
cRZ2FXfXa7wxkqOe0B2Z94eNRIoFj2E/XGQzX7B7l3OqQg+Uv1wIDAQAB"""
            }
        )


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
