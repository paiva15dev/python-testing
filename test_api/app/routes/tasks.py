from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)


def get_task_or_404(task_id, user_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None, jsonify({"error": "Tarefa nao encontrada"}), 404
    if task.user_id != user_id:
        return None, jsonify({"error": "Acesso negado"}), 403
    return task, None, None


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def list_tasks():
    """
    Lista todas as tarefas do usuario logado
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: query
        name: done
        type: boolean
        description: Filtrar por status (true ou false)
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 10
    responses:
      200:
        description: Lista de tarefas
      401:
        description: Token ausente ou invalido
    """
    user_id = int(get_jwt_identity())
    query = Task.query.filter_by(user_id=user_id)

    done_param = request.args.get("done")
    if done_param is not None:
        query = query.filter_by(done=done_param.lower() == "true")

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "tasks": [t.to_dict() for t in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page,
    }), 200


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    """
    Cria uma nova tarefa
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Estudar Flask
            description:
              type: string
              example: Ver a documentacao oficial
    responses:
      201:
        description: Tarefa criada com sucesso
      400:
        description: Titulo obrigatorio
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("title", "").strip():
        return jsonify({"error": "O campo title e obrigatorio"}), 400

    task = Task(
        title=data["title"].strip(),
        description=data.get("description", "").strip() or None,
        done=False,
        user_id=user_id,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Tarefa criada com sucesso",
        "task": task.to_dict()
    }), 201


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """
    Retorna uma tarefa especifica
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Dados da tarefa
      404:
        description: Tarefa nao encontrada
    """
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """
    Atualiza uma tarefa
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
              example: Novo titulo
            description:
              type: string
              example: Nova descricao
            done:
              type: boolean
              example: true
    responses:
      200:
        description: Tarefa atualizada
      404:
        description: Tarefa nao encontrada
    """
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status

    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400

    if "title" in data:
        if not data["title"].strip():
            return jsonify({"error": "O titulo nao pode ser vazio"}), 400
        task.title = data["title"].strip()

    if "description" in data:
        task.description = data["description"].strip() or None

    if "done" in data:
        if not isinstance(data["done"], bool):
            return jsonify({"error": "done deve ser true ou false"}), 400
        task.done = data["done"]

    db.session.commit()
    return jsonify({
        "message": "Tarefa atualizada com sucesso",
        "task": task.to_dict()
    }), 200


@tasks_bp.route("/<int:task_id>/toggle", methods=["PATCH"])
@jwt_required()
def toggle_task(task_id):
    """
    Inverte o status done da tarefa
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Status alterado
      404:
        description: Tarefa nao encontrada
    """
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status

    task.done = not task.done
    db.session.commit()

    status_text = "concluida" if task.done else "pendente"
    return jsonify({
        "message": f"Tarefa marcada como {status_text}",
        "task": task.to_dict()
    }), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """
    Deleta uma tarefa
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Tarefa deletada
      404:
        description: Tarefa nao encontrada
    """
    user_id = int(get_jwt_identity())
    task, err, status = get_task_or_404(task_id, user_id)
    if err:
        return err, status

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Tarefa deletada com sucesso"}), 200