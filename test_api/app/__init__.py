from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Todo API",
        "description": "API de tarefas com autenticacao JWT",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Cole o token assim: Bearer SEU_TOKEN"
        }
    }
}

swagger_config = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}


def create_app(env="development"):
    app = Flask(__name__)
    app.config.from_object(config[env])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    Swagger(app, template=swagger_template, config=swagger_config)

    @jwt.unauthorized_loader
    def unauthorized_response(reason):
        return jsonify({"error": "Token ausente ou invalido", "detail": reason}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token expirado. Faca login novamente"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(reason):
        return jsonify({"error": "Token invalido", "detail": reason}), 422

    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app