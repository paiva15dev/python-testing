from flask import jsonify, request


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Requisicao invalida"}), 400

    # @app.errorhandler(404)
    # def not_found(e):
    #     return jsonify({"error": "Recurso nao encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Metodo nao permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Erro interno do servidor"}), 500