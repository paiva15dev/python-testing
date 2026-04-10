from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required = ["username", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatorios: {', '.join(missing)}"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username ja esta em uso"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email ja esta em uso"}), 409

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Usuario criado com sucesso",
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username e password sao obrigatorios"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Credenciais invalidas"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login realizado com sucesso",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"error": "Usuario nao encontrado"}), 404

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    data = request.get_json()

    if not data.get("current_password") or not data.get("new_password"):
        return jsonify({"error": "current_password e new_password sao obrigatorios"}), 400

    if not user.check_password(data["current_password"]):
        return jsonify({"error": "Senha atual incorreta"}), 401

    if len(data["new_password"]) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400

    user.set_password(data["new_password"])
    db.session.commit()

    return jsonify({"message": "Senha alterada com sucesso"}), 200  