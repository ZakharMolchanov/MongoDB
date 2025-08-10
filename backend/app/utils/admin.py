from flask import current_app, jsonify
from functools import wraps
from app.models.user import User

def _is_admin(user):
    emails = current_app.config.get("ADMIN_EMAILS", "")
    admin_emails = {e.strip().lower() for e in emails.split(",") if e.strip()}
    return (user.email or "").lower() in admin_emails

def require_admin(fn):
    @wraps(fn)
    def wrapper(user_id, *args, **kwargs):
        user = User.query.get(user_id)
        if not user or not _is_admin(user):
            return jsonify({"error": "Admin only"}), 403
        return fn(user_id, *args, **kwargs)
    return wrapper
