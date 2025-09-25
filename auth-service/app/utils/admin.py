import requests
from flask import jsonify
from functools import wraps

AUTH_SERVICE_URL = "http://auth-service:5001"  # имя контейнера в docker-compose

def is_admin(user_id):
    try:
        r = requests.get(f"{AUTH_SERVICE_URL}/admin/check/{user_id}")
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
