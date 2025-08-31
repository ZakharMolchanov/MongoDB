
from flask import Blueprint, jsonify, request
from app.models.query import Query
from app.utils.auth import token_required

history_bp = Blueprint("history", __name__, url_prefix="/assignments")

@history_bp.route("/<int:assignment_id>/attempts", methods=["GET"])
@token_required
def get_attempts(user_id, assignment_id):
    """
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
    """
    limit = max(1, min(int(request.args.get("limit", 20)), 100))
    offset = max(0, int(request.args.get("offset", 0)))

    q = (Query.query
         .filter_by(user_id=user_id, assignment_id=assignment_id)
         .order_by(Query.created_at.desc())
         .offset(offset).limit(limit).all())

    return jsonify([{
        "query_id": it.query_id,
        "created_at": it.created_at.isoformat(),
        "status": it.status,
        "exec_ms": it.exec_ms,
        "result_count": it.result_count,
        "error_message": it.error_message,
        "code": it.query_text,       # сырой shell-код
    } for it in q])
