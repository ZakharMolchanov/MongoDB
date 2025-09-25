from flask import Blueprint, jsonify
from app.utils.auth import token_required
from bson import json_util
import requests

schema_bp = Blueprint("schema", __name__, url_prefix="/assignments")

@schema_bp.route("/<int:assignment_id>/schema", methods=["GET"])
@token_required
def get_schema(user_id, assignment_id):
    """
    Получить список коллекций и пример документов для базы пользователя
    ---
    tags: [Schema]
    parameters:
      - in: path
        name: assignment_id
        type: integer
        required: true
    responses:
      200:
        description: Схема БД (коллекции + примеры документов)
    """
    # Получаем имя базы данных для пользователя
    db_name = f"db_user_{user_id}"

    # Подключаем Mongo через flask_pymongo
    from app import mongo

    # Получаем подключение к базе
    db = mongo.cx[db_name]

    result = {}
    try:
        # Получаем список коллекций в базе
        collections = db.list_collection_names()
        for coll in collections:
            # Берём максимум 3 документа для примера
            docs = list(db[coll].find({}).limit(3))
            result[coll] = json_util.loads(json_util.dumps(docs))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)
