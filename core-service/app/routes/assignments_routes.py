from flask import Blueprint, jsonify, request
from app import db
from app.models.assignment import Assignment
from app.models.assignment_test import AssignmentTest
from app.utils.auth import token_required
from app.utils.admin import is_admin  # Используем is_admin для проверки прав
from app.models.topic import Topic
from sqlalchemy.exc import SQLAlchemyError


def _safe_rollback():
    try:
        db.session.rollback()
    except Exception:
        try:
            db.session.remove()
        except Exception:
            pass

assignments_bp = Blueprint("assignments", __name__, url_prefix="/assignments")


# GET /assignments — список всех заданий (для админки)
@assignments_bp.route("", methods=["GET"])
@token_required
def list_assignments(user_id):
    # optional filters: q (search title/description), topic_id
    q = request.args.get('q')
    topic_id = request.args.get('topic_id')
    qry = Assignment.query
    if q:
        like = f"%{q}%"
        qry = qry.filter((Assignment.title.ilike(like)) | (Assignment.description.ilike(like)))
    if topic_id:
        try:
            tid = int(topic_id)
            qry = qry.filter(Assignment.topic_id == tid)
        except Exception:
            pass
    items = qry.order_by(Assignment.assignment_id.asc()).all()
    return jsonify([{
        "assignment_id": a.assignment_id,
        "topic_id": a.topic_id,
        "title": a.title,
        "description": a.description,
        "difficulty": a.difficulty,
        "created_at": a.created_at.isoformat(),
        "schema": a.schema_json
    } for a in items])

# GET /assignments/<assignment_id>
@assignments_bp.route("/<int:assignment_id>", methods=["GET"])
@token_required
def get_assignment(user_id, assignment_id):
    a = Assignment.query.get(assignment_id)
    if not a:
        return jsonify({"error": "Assignment not found"}), 404

    return jsonify({
        "assignment_id": a.assignment_id,
        "topic_id": a.topic_id,
        "title": a.title,
        "description": a.description,
        "difficulty": a.difficulty,
        "created_at": a.created_at.isoformat(),
        "schema": a.schema_json,  # Показываем схему задания
        "tests": [
            {
                "test_id": t.test_id,
                "test_description": t.test_description
            } for t in a.tests
        ]
    })

# POST /assignments — создать задание
@assignments_bp.route("", methods=["POST"])
@token_required
def create_assignment(user_id):
    # Проверка прав администратора
    if not is_admin(user_id):
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(force=True)
    if not data.get("topic_id") or not data.get("title"):
        return jsonify({"error": "Missing required fields"}), 400

    # validate topic exists
    topic = Topic.query.get(data["topic_id"])
    if not topic:
        return jsonify({"error": "Topic not found"}), 404

    a = Assignment(
        topic_id=data["topic_id"],
        title=data["title"],
        description=data.get("description"),
        difficulty=data.get("difficulty"),
        schema_json=data.get("schema")  # Сохраняем схему
    )
    try:
        db.session.add(a)
        db.session.flush()
    except SQLAlchemyError as e:
        _safe_rollback()
        return jsonify({"error": "Database error creating assignment", "details": str(e)}), 500

    for t in data.get("tests", []):
        db.session.add(AssignmentTest(
            assignment_id=a.assignment_id,
            expected_result=t.get("expected_result", "[]"),
            test_description=t.get("test_description", "")
        ))

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        _safe_rollback()
        return jsonify({"error": "Database error committing assignment", "details": str(e)}), 500

    return jsonify({"message": "Assignment created", "assignment_id": a.assignment_id}), 201

# PUT /assignments/<assignment_id> — обновить задание
@assignments_bp.route("/<int:assignment_id>", methods=["PUT"])
@token_required
def update_assignment(user_id, assignment_id):
    # Проверка прав администратора
    if not is_admin(user_id):
        return jsonify({"error": "Admin only"}), 403

    a = Assignment.query.get(assignment_id)
    if not a:
        return jsonify({"error": "Assignment not found"}), 404

    data = request.get_json(force=True)
    if "title" in data: a.title = data["title"]
    if "description" in data: a.description = data["description"]
    if "difficulty" in data: a.difficulty = data["difficulty"]
    if "schema" in data: a.schema_json = data["schema"]

    if "tests" in data:
        for old in a.tests:
            db.session.delete(old)
        for t in data["tests"] or []:
            db.session.add(AssignmentTest(
                assignment_id=a.assignment_id,
                expected_result=t.get("expected_result", "[]"),
                test_description=t.get("test_description", "")
            ))

    db.session.commit()
    return jsonify({"message": "Assignment updated"})
