from flask.views import MethodView
from flask import request, jsonify
from services.vote_processing_services import process_gavt


class DuplicateSelectorController(MethodView):
    def post(self):
        gavt = request.get_json()

        if not isinstance(gavt, list):
            return jsonify({"error": "Esperado lista de votos"}), 400

        result = process_gavt(gavt)

        return jsonify({"message": "Duplicatas processadas e salvas", **result}), 200
