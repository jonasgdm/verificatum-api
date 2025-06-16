import requests

BASE_URL = "http://localhost:8080/verificatum"


def post_setup(payload=None):
    return _post("/setup", payload)


def post_keygen(payload=None):
    return _post("/keygen", payload)


def post_generate_ciphertexts(payload=None):
    return _post("/generate-ciphertexts", payload)


def post_mix(payload=None):
    return _post("/mix", payload)


def post_verify(payload=None):
    return _post("/verify", payload)


def _post(endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Erro] Falha na requisição para {url}: {e}")
        return None
