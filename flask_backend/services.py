import requests

VERIFICATUM_API_BASE_URL = "http://localhost:8080"


class VerificatumApiService:

    @staticmethod
    def status():
        try:
            response = requests.post(f"{VERIFICATUM_API_BASE_UR}/keygen")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /keygen: {str(e)}"}

    @staticmethod
    def mix():
        try:
            response = requests.post(f"{API_BASE_URL}/mix")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": True, "message": f"Erro ao chamar /mix: {str(e)}"}
