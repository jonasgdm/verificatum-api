from flask import Blueprint
from controller import *


routes_bp = Blueprint("routes", __name__)

routes_bp.add_url_rule(
    "/api/publicKey", view_func=PublicKeyController.as_view("publicKey")
)

routes_bp.add_url_rule("/api/GAVT", view_func=GAVTController.as_view("GAVT"))
routes_bp.add_url_rule(
    "/api/processGAVT", view_func=ProcessGAVTController.as_view("processGAVT")
)

routes_bp.add_url_rule(
    "/api/shuffle/<int:index>", view_func=ShuffleController.as_view("shuffle")
)
