import requests

BASE_URL = "http://127.0.0.1:5000/api"


def post_gavt(file_path):
    return _post("/GAVT", file_path)


def _post(endpoint, file_path):
    url = f"{BASE_URL}{endpoint}"
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}

            response = requests.post(url, files=files)
            response.raise_for_status()
            return response.json()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição para {url}: {e}")
        return None
