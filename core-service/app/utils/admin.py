import requests
from flask import jsonify, request
from functools import wraps

AUTH_SERVICE_URL = "http://auth-service:5001"


def is_admin(user_id):
    """Query auth-service to check whether a user is admin.

    Forwards the incoming Authorization header so auth-service can validate the token.
    """
    try:
        auth = request.headers.get('Authorization')
        headers = {'Authorization': auth} if auth else {}
        r = requests.get(f"{AUTH_SERVICE_URL}/auth/is-admin/{user_id}", headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get("is_admin", False)
    except Exception as e:
        print(f"[core-service] Ошибка при запросе к auth-service: {e}")
    return False


def require_admin(fn):
    @wraps(fn)
    def wrapper(user_id, *args, **kwargs):
        if not is_admin(user_id):
            return jsonify({"error": "Admin only"}), 403
        return fn(user_id, *args, **kwargs)

    return wrapper
