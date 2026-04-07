# ── PATCH /tasks/<id>/toggle ──────────────────────────────────────────────────
 
@tasks_bp.route("/<int:task_id>/toggle", methods=["PATCH"])
@jwt_required()
def toggle_task(task_id):
    """Atalho para marcar/desmarcar uma tarefa como concluída."""
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status
 
    task.done = not task.done
    db.session.commit()
 
    status_text = "concluída" if task.done else "pendente"
    return jsonify({
        "message": f"Tarefa marcada como {status_text}",
        "task": task.to_dict()
    }), 200
 
 
# ── DELETE /tasks/<id> ────────────────────────────────────────────────────────
 
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """Deleta uma tarefa permanentemente."""
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status
 
    db.session.delete(task)
    db.session.commit()
 
    return jsonify({"message": "Tarefa deletada com sucesso"}), 200