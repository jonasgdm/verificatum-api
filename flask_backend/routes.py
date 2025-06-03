from flask import Blueprint
from controller import *


routes_bp = Blueprint("routes", __name__)

routes_bp.add_url_rule("/api/setup", view_func=SetupController.as_view("setup"))
routes_bp.add_url_rule("/api/keygen", view_func=KeyGenController.as_view("keygen"))
routes_bp.add_url_rule(
    "/api/generate-ciphertexts",
    view_func=GenerateCyphertextsController.as_view("generate-cyphertexts"),
)
routes_bp.add_url_rule(
    "/api/mix",
    view_func=MixController.as_view("mix"),
)
routes_bp.add_url_rule(
    "/api/verify",
    view_func=MixController.as_view("verify"),
)


routes_bp.add_url_rule("/api/mock", view_func=AVTMockController.as_view("mock"))
# routes_bp.add_url_rule(
#     "/api/cyphertexts", view_func=CypherTextController.as_view("cyphertexts")
# )
routes_bp.add_url_rule("/api/mix/1", view_func=Mix1Controller.as_view("mix1"))
routes_bp.add_url_rule("/api/mix/2", view_func=Mix2Controller.as_view("mix2"))
routes_bp.add_url_rule("/api/keys", view_func=KeysController.as_view("keys"))
routes_bp.add_url_rule("/api/decode", view_func=DecodeController.as_view("decode"))
