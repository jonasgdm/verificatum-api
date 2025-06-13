from flask import Blueprint
from controller import *


routes_bp = Blueprint("routes", __name__)

routes_bp.add_url_rule(
    "/api/publicKey", view_func=PublicKeyController.as_view("publicKey")
)

routes_bp.add_url_rule("/api/GAVT", view_func=GAVTController.as_view("GAVT"))

# ------------------------------------------------------------------------------

routes_bp.add_url_rule(
    "/api/ciphertexts01",
    view_func=Cypher01Controller.as_view("cypher01"),
)
routes_bp.add_url_rule(
    "/api/ciphertexts02",
    view_func=Cypher02Controller.as_view("cypher02"),
)

routes_bp.add_url_rule("/api/mix/1", view_func=Mix1Controller.as_view("mix1"))
routes_bp.add_url_rule("/api/mix/2", view_func=Mix2Controller.as_view("mix2"))
routes_bp.add_url_rule("/api/keys", view_func=KeysController.as_view("keys"))
routes_bp.add_url_rule("/api/decode", view_func=DecodeController.as_view("decode"))
