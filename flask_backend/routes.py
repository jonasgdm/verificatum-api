from flask import Blueprint
from controller import StatusController
from controller import KeyGenController

routes_bp = Blueprint("routes", __name__)


routes_bp.add_url_rule("/api/setup", view_func=StatusController.as_view("setup"))
