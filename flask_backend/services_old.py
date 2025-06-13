import requests
import random
import string

VERIFICATUM_API_BASE_URL = "http://localhost:8080/verificatum"
# Escolher se vai usar um mock para as requests, enquanto API nao eh finalizada
USE_MOCK = False


class VerificatumApiService:

    @staticmethod
    def get_key():
        try:
            with open("../verificatum-demo/01/publicKey", "rb") as f:
                key_bytes = f.read()
            return list(key_bytes)
        except FileNotFoundError:
            return {"error": True, "message": "Arquivo publicKey não encontrado."}
        except Exception as e:
            return {"error": True, "message": f"Erro ao ler publicKey: {str(e)}"}
