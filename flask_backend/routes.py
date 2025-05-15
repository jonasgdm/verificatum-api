from flask import Blueprint
from controller import *


routes_bp = Blueprint("routes", __name__)


routes_bp.add_url_rule("/api/mock", view_func=MockController.as_view("mock"))
routes_bp.add_url_rule(
    "/api/cyphertexts", view_func=CypherTextController.as_view("cyphertexts")
)
routes_bp.add_url_rule("/api/mix/1", view_func=Mix1Controller.as_view("mix1"))
routes_bp.add_url_rule("/api/mix/2", view_func=Mix2Controller.as_view("mix2"))
routes_bp.add_url_rule("/api/keys", view_func=KeysController.as_view("keys"))
routes_bp.add_url_rule("/api/decode", view_func=DecodeController.as_view("decode"))
