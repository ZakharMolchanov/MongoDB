import bcrypt
import jwt
from flask import current_app, request, jsonify
from functools import wraps
from datetime import datetime, timedelta


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_access_token(user_id):
    payload = {
        "sub": str(user_id),  # Делаем строкой
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    secret = current_app.config.get("SECRET_KEY")
    print(f"[DEBUG] Generating token with SECRET_KEY={secret}")
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token):
    secret = current_app.config.get("SECRET_KEY")
    print(f"[DEBUG] Decoding token with SECRET_KEY={secret}")
    return jwt.decode(token, secret, algorithms=["HS256"])


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = decode_token(token)
            user_id = decoded["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            print(f"[DEBUG] Invalid token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(user_id, *args, **kwargs)

    return decorated
