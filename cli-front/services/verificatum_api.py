import requests

BASE_URL = "http://localhost:8080"


def post_setup():
    payload = {"servers": ["$USER@127.0.0.1", "$USER@127.0.0.1"]}
    return _post("/guardian/setup?auto=true&numServers=3", payload)


def post_keygen(payload=None):
    return _post("/guardian/keygen", payload)


def get_publickey():
    return _get("/guardian/public-key")


def get_log():
    return _get("/shuffler/log")


def decrypt():
    return _post("/guardian/decrypt")


def get_shuffled():
    return _get("/shuffler/shuffled-ciphertexts")


def _post(endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição para {url}: {e}")
        return None


def _get(endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.text
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição para {url}: {e}")
        return None
