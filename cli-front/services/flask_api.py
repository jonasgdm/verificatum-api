import requests

BASE_URL = "http://127.0.0.1:5000/api"


def post_gavt(file_path):
    return _post_file("/GAVT", file_path)


def process_gavt():
    return _post("/processGAVT")


def _post_file(endpoint, file_path):
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


def _post(endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição para {url}: {e}")
        return None
