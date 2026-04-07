def me():
    """
    Retorna os dados do usuário autenticado.
    Requer header: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
 
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
 
    return jsonify({"user": user.to_dict()}), 200
 
 
@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    Altera a senha do usuário autenticado.
    Body JSON: { "current_password": "...", "new_password": "..." }
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    data = request.get_json()
 
    if not data.get("current_password") or not data.get("new_password"):
        return jsonify({"error": "current_password e new_password são obrigatórios"}), 400
 
    if not user.check_password(data["current_password"]):
        return jsonify({"error": "Senha atual incorreta"}), 401
 
    if len(data["new_password"]) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400
 
    user.set_password(data["new_password"])
    db.session.commit()
 
    return jsonify({"message": "Senha alterada com sucesso"}), 200
 