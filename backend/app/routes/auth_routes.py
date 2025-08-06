from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.utils.auth import hash_password, verify_password, generate_access_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")

    if not all([email, first_name, last_name, password]):
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=hash_password(password)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_access_token(user.id)
    return jsonify({"access_token": token})


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat()
    })
