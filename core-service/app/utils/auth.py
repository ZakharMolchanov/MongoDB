import requests
from flask import request, jsonify, g
from functools import wraps

AUTH_SERVICE_URL = "http://auth-service:5001"


def token_required(f):
    """Decorator: validate token by asking auth-service for /auth/me.

    Forwards the Authorization header to auth-service; if auth-service returns 200,
    we extract `id` from its JSON and pass it as user_id to the wrapped function.
    This keeps token secret validation centralised in auth-service.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        try:
            headers = {"Authorization": auth_header}
            r = requests.get(f"{AUTH_SERVICE_URL}/auth/me", headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                user_id = data.get("id")
                if user_id is None:
                    return jsonify({"error": "Invalid token (no user)"}), 401
                try:
                    g.user_id = user_id
                except Exception:
                    pass
                return f(user_id, *args, **kwargs)
            # forward 401/403 from auth-service as unauthorized
            if r.status_code in (401, 403):
                return jsonify({"error": "Missing or invalid token"}), 401
        except requests.RequestException as e:
            print(f"[core-service] token validation error: {e}")
            return jsonify({"error": "Auth service unreachable"}), 503

        return jsonify({"error": "Missing or invalid token"}), 401

    return decorated
