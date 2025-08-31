from flask import Blueprint, jsonify, request
from bson import ObjectId
from copy import deepcopy
from app import db, mongo
from app.models.assignment import Assignment
from app.models.assignment_test import AssignmentTest
from app.models.query import Query
from app.models.completed_assignment import CompletedAssignment
from app.utils.auth import token_required
from app.utils.admin import require_admin
import json

assignments_bp = Blueprint("assignments", __name__, url_prefix="/assignments")


# GET /assignments/<assignment_id> — задание + тесты
@assignments_bp.route("/<int:assignment_id>", methods=["GET"])
@token_required
def get_assignment(user_id, assignment_id):
    """
    Получить задание по ID
    ---
    tags:
      - Assignments
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: assignment_id
        type: integer
        required: true
        description: ID задания
    responses:
      200:
        description: Информация о задании
      404:
        description: Задание не найдено
    """
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
        "tests": [
            {
                "test_id": t.test_id,
                "test_description": t.test_description
            } for t in a.tests
        ]
    })


# POST /assignments — создать задание (админ)
@assignments_bp.route("", methods=["POST"])
@token_required
@require_admin
def create_assignment(user_id):
    """
    Создать новое задание
    ---
    tags:
      - Assignments
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - topic_id
            - title
          properties:
            topic_id:
              type: integer
            title:
              type: string
            description:
              type: string
            difficulty:
              type: string
            tests:
              type: array
              items:
                type: object
                properties:
                  expected_result:
                    type: string
                  test_description:
                    type: string
    responses:
      201:
        description: Задание создано
    """
    data = request.get_json(force=True)
    required = ("topic_id", "title")
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    a = Assignment(
        topic_id=data["topic_id"],
        title=data["title"],
        description=data.get("description"),
        difficulty=data.get("difficulty")
    )
    db.session.add(a)
    db.session.flush()

    for t in data.get("tests", []):
        test = AssignmentTest(
            assignment_id=a.assignment_id,
            expected_result=t.get("expected_result", "[]"),
            test_description=t.get("test_description", "")
        )
        db.session.add(test)

    db.session.commit()
    return jsonify({"message": "Assignment created", "assignment_id": a.assignment_id}), 201


# PUT /assignments/<assignment_id> — обновить задание (админ)
@assignments_bp.route("/<int:assignment_id>", methods=["PUT"])
@token_required
@require_admin
def update_assignment(user_id, assignment_id):
    """
    Обновить задание по ID
    ---
    tags:
      - Assignments
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: assignment_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
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
            tests:
              type: array
              items:
                type: object
                properties:
                  expected_result:
                    type: string
                  test_description:
                    type: string
    responses:
      200:
        description: Задание обновлено
      404:
        description: Задание не найдено
    """
    a = Assignment.query.get(assignment_id)
    if not a:
        return jsonify({"error": "Assignment not found"}), 404

    data = request.get_json(force=True)

    if "topic_id" in data and data["topic_id"]:
        a.topic_id = data["topic_id"]
    if "title" in data and data["title"]:
        a.title = data["title"]
    if "description" in data:
        a.description = data["description"]
    if "difficulty" in data:
        a.difficulty = data["difficulty"]

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


# DELETE /assignments/<assignment_id> — удалить задание (админ)
@assignments_bp.route("/<int:assignment_id>", methods=["DELETE"])
@token_required
@require_admin
def delete_assignment(user_id, assignment_id):
    """
    Удалить задание по ID
    ---
    tags:
      - Assignments
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: assignment_id
        type: integer
        required: true
    responses:
      200:
        description: Задание удалено
      404:
        description: Задание не найдено
    """
    a = Assignment.query.get(assignment_id)
    if not a:
        return jsonify({"error": "Assignment not found"}), 404

    db.session.delete(a)
    db.session.commit()
    return jsonify({"message": "Assignment deleted"})

@assignments_bp.route("", methods=["GET"])
@token_required
def list_assignments(user_id):
    """
    ---
    tags: [Assignments]
    summary: Получить список всех заданий с темами
    responses:
      200:
        schema:
          type: array
          items:
            type: object
    """
    # Лёгкий join по теме
    q = db.session.query(
        Assignment.assignment_id,
        Assignment.title,
        Assignment.description,
        Assignment.difficulty,
        Assignment.created_at,
        Topic.topic_id,
        Topic.title.label("topic_title"),
    ).join(Topic, Topic.topic_id == Assignment.topic_id).order_by(Topic.topic_id, Assignment.assignment_id)

    items = []
    for a in q.all():
        items.append({
            "assignment_id": a.assignment_id,
            "title": a.title,
            "description": a.description,
            "difficulty": a.difficulty,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "topic": {
                "topic_id": a.topic_id,
                "title": a.topic_title
            }
        })
    return jsonify(items), 200