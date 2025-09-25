from flask import Blueprint, jsonify, request
from app import db
from app.models.topic import Topic
from app.utils.auth import token_required
from app.utils.admin import is_admin  # Используем is_admin для проверки прав

topics_bp = Blueprint("topics", __name__, url_prefix="/topics")


# GET /topics — список тем
@topics_bp.route("", methods=["GET"])
@token_required
def list_topics(user_id):
    """
    Получить список всех тем
    ---
    tags:
      - Topics
    security:
      - BearerAuth: []
    responses:
      200:
        description: Список тем
        schema:
          type: array
          items:
            type: object
            properties:
              topic_id:
                type: integer
              title:
                type: string
              description:
                type: string
              difficulty:
                type: string
              created_at:
                type: string
                format: date-time
    """
    # optional filters: q (search in title/description), difficulty
    q = request.args.get('q')
    difficulty = request.args.get('difficulty')
    qry = Topic.query
    if q:
        like = f"%{q}%"
        qry = qry.filter((Topic.title.ilike(like)) | (Topic.description.ilike(like)))
    if difficulty:
        qry = qry.filter(Topic.difficulty == difficulty)
    items = qry.order_by(Topic.topic_id.asc()).all()
    return jsonify([{
        "topic_id": t.topic_id,
        "title": t.title,
        "description": t.description,
        "difficulty": t.difficulty,
        "created_at": t.created_at.isoformat()
    } for t in items])


# GET /topics/<topic_id> — тема + задания
@topics_bp.route("/<int:topic_id>", methods=["GET"])
@token_required
def get_topic(user_id, topic_id):
    """
    Получить информацию по теме и список её заданий
    ---
    tags:
      - Topics
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: topic_id
        type: integer
        required: true
        description: ID темы
    responses:
      200:
        description: Информация по теме
      404:
        description: Тема не найдена
    """
    t = Topic.query.get(topic_id)
    if not t:
        return jsonify({"error": "Topic not found"}), 404

    return jsonify({
        "topic_id": t.topic_id,
        "title": t.title,
        "description": t.description,
        "difficulty": t.difficulty,
        "created_at": t.created_at.isoformat(),
        "assignments": [
            {
                "assignment_id": a.assignment_id,
                "title": a.title,
                "description": a.description,
                "difficulty": a.difficulty
            } for a in t.assignments
        ]
    })


# POST /topics — создать тему (только для администраторов)
@topics_bp.route("", methods=["POST"])
@token_required
def create_topic(user_id):
    """
    Создать новую тему
    ---
    tags:
      - Topics
    security:
      - BearerAuth: []
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
            description:
              type: string
            difficulty:
              type: string
    responses:
      201:
        description: Тема создана
      400:
        description: Ошибка валидации
    """
    # Проверяем права администратора
    if not is_admin(user_id):
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(force=True)
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    t = Topic(
        title=title,
        description=data.get("description"),
        difficulty=data.get("difficulty")
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"message": "Topic created", "topic_id": t.topic_id}), 201


# PUT /topics/<topic_id> — обновить тему (только для администраторов)
@topics_bp.route("/<int:topic_id>", methods=["PUT"])
@token_required
def update_topic(user_id, topic_id):
    """
    Обновить тему
    ---
    tags:
      - Topics
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: topic_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            difficulty:
              type: string
    responses:
      200:
        description: Тема обновлена
      404:
        description: Тема не найдена
    """
    # Проверяем права администратора
    if not is_admin(user_id):
        return jsonify({"error": "Admin only"}), 403

    t = Topic.query.get(topic_id)
    if not t:
        return jsonify({"error": "Topic not found"}), 404

    data = request.get_json(force=True)
    if "title" in data and data["title"]:
        t.title = data["title"]
    if "description" in data:
        t.description = data["description"]
    if "difficulty" in data:
        t.difficulty = data["difficulty"]
    db.session.commit()
    return jsonify({"message": "Topic updated"})


# DELETE /topics/<topic_id> — удалить тему (только для администраторов)
@topics_bp.route("/<int:topic_id>", methods=["DELETE"])
@token_required
def delete_topic(user_id, topic_id):
    """
    Удалить тему
    ---
    tags:
      - Topics
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: topic_id
        type: integer
        required: true
    responses:
      200:
        description: Тема удалена
      404:
        description: Тема не найдена
    """
    # Проверяем права администратора
    if not is_admin(user_id):
        return jsonify({"error": "Admin only"}), 403

    t = Topic.query.get(topic_id)
    if not t:
        return jsonify({"error": "Topic not found"}), 404

    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Topic deleted"})
