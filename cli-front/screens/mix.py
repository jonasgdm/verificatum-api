# import subprocess
from services import flask_api


# def cifrar(voto):
#     subprocess.run(["node", "encrypt.js", voto], check=True)
#     with open("ciphertext.bt", "rb") as f:
#         return f.read()


def show():
    flask_api.post_gavt("output/gavt.json")
