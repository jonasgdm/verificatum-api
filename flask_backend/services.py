import requests
import random
import string

VERIFICATUM_API_BASE_URL = "http://localhost:8080/verificatum"
# Escolher se vai usar um mock para as requests, enquanto API nao eh finalizada
USE_MOCK = False


class VerificatumApiService:

    @staticmethod
    def setup():
        try:
            response = requests.post(f"{VERIFICATUM_API_BASE_URL}/setup")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /setup: {str(e)}"}

    @staticmethod
    def keygen():
        try:
            response = requests.post(f"{VERIFICATUM_API_BASE_URL}/keygen")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /setup: {str(e)}"}

    @staticmethod
    def get_key():
        try:
            with open("../verificatum-demo/logs/publicKey", "r") as f:
                return {"publicKey": f.read()}
        except FileNotFoundError:
            return {"error": True, "message": "Arquivo publicKey não encontrado."}
        except Exception as e:
            return {"error": True, "message": f"Erro ao ler publicKey: {str(e)}"}

    @staticmethod
    def cyphertexts():
        try:
            if USE_MOCK:
                return {
                    "votos": [
                        "a8f43b9c",
                        "bd9247ef",
                        "c13098ab",
                        "dcef0912",
                        "e9a412fb",
                        "f1b3aa99",
                    ]
                }
            response = requests.post(f"{VERIFICATUM_API_BASE_URL}/generate-ciphertexts")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /cyphertexts: {str(e)}"}

    @staticmethod
    def mix():
        try:
            if USE_MOCK:
                votos = [
                    "".join(random.choices(string.hexdigits.lower(), k=8))
                    for _ in range(6)
                ]
                return {"votos": votos}
            response = requests.post(f"{VERIFICATUM_API_BASE_URL}/mix")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /mix: {str(e)}"}

    @staticmethod
    def verify():
        try:
            response = requests.post(f"{VERIFICATUM_API_BASE_URL}/verify")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /verify: {str(e)}"}

    @staticmethod
    def cypher(voteslist):
        try:
            if USE_MOCK:
                pass
            # response = requests.post(f"{API_BASE_URL}/mix")
            # response.raise_for_status()
            # return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /mix: {str(e)}"}
