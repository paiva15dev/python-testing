
Copiar

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
 
from config import config
 
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
 
 
def create_app(env="development"):
    app = Flask(__name__)
    app.config.from_object(config[env])
 
    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
 
    # Respostas de erro do JWT em JSON
    @jwt.unauthorized_loader
    def unauthorized_response(reason):
        return jsonify({"error": "Token ausente ou inválido", "detail": reason}), 401
 
    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token expirado. Faça login novamente"}), 401
 
    @jwt.invalid_token_loader
    def invalid_token_response(reason):
        return jsonify({"error": "Token inválido", "detail": reason}), 422
 
    # Registra blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
 
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
 
    # Registra handlers de erro globais
    from app.errors import register_error_handlers
    register_error_handlers(app)
 
    return app