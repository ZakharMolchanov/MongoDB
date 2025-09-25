from flask import Blueprint, jsonify, request
from app.models.query import Query
from app.utils.auth import token_required  # для проверки токенов
from sqlalchemy import or_

history_bp = Blueprint("history", __name__, url_prefix="/assignments")

@history_bp.route("/<int:assignment_id>/attempts", methods=["GET"])
@token_required
def get_attempts(user_id, assignment_id):
    """
    История попыток пользователя по заданию
    ---
    tags: [Attempts]
    summary: История попыток пользователя по заданию
    parameters:
      - in: path
        name: assignment_id
        type: integer
        required: true
      - in: query
        name: limit
        type: integer
        default: 20
      - in: query
        name: offset
        type: integer
        default: 0
    responses:
      200:
        description: Список попыток пользователя
        schema:
          type: array
          items:
            type: object
            properties:
              query_id:
                type: integer
              created_at:
                type: string
                format: date-time
              status:
                type: string
              exec_ms:
                type: integer
              result_count:
                type: integer
              error_message:
                type: string
              code:
                type: string
    """
    limit = max(1, min(int(request.args.get("limit", 20)), 100))
    offset = max(0, int(request.args.get("offset", 0)))

    # Получаем все запросы для текущего пользователя и задания.
    # Also include fallback attempts saved without user_id (NULL) so UI can show
    # results when DB saved a minimal Query without FK (older deployments).
    q = (Query.query
      .filter(or_(Query.user_id == user_id, Query.user_id == None), Query.assignment_id == assignment_id)
      .order_by(Query.created_at.desc())
      .offset(offset).limit(limit).all())

    # Возвращаем историю попыток
    return jsonify([{
        "query_id": it.query_id,
        "id": it.query_id,
        "created_at": it.created_at.isoformat() if it.created_at else None,
        "status": it.status,
        "exec_ms": it.exec_ms,
        "result_count": it.result_count,
        "error_message": it.error_message,
        "code": it.query_text,  # Сырой shell-код
    } for it in q])
