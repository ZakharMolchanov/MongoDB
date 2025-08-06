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
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS25 6")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split(" ")[1]
        try:
            decoded = decode_token(token)
            user_id = decoded["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(user_id, *args, **kwargs)

    return decorated
