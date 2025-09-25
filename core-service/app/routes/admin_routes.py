from flask import Blueprint, jsonify, request
from app import db
from app.models.request_log import RequestLog
from app.utils.auth import token_required
from app.utils.admin import require_admin
import requests
from sqlalchemy.exc import SQLAlchemyError, NoReferencedTableError, ProgrammingError

ADMIN_BP = Blueprint('admin', __name__, url_prefix='/admin')

AUTH_SERVICE = 'http://auth-service:5001'


@ADMIN_BP.route('/logs', methods=['GET'])
@token_required
@require_admin
def list_logs(user_id):
    limit = min(int(request.args.get('limit', 50)), 200)
    offset = max(0, int(request.args.get('offset', 0)))
    try:
        q = RequestLog.query.order_by(RequestLog.created_at.desc()).offset(offset).limit(limit).all()
        return jsonify([r.to_dict() for r in q])
    except (NoReferencedTableError, ProgrammingError) as e:
        # missing table(s) — provide actionable, concise message
        print(f"[admin_routes] DB schema issue listing logs: {e}")
        # Return success with empty list and a warning so frontend can continue to render
        return jsonify({
            "data": [],
            "warning": "Database schema not initialized: RequestLog table missing. Run DB migrations or create tables. See /docker/init_postgres.sql",
            "remediation": "Run docker-compose down; remove anonymous volumes if reinitializing, or execute the SQL migration/ALTER TABLE to add missing tables/columns.",
        }), 200
    except SQLAlchemyError as e:
        # other DB errors: return concise message and log details
        print(f"[admin_routes] SQL error listing logs: {e}")
        return jsonify({"error": "Database error while listing logs", "details": str(e)}), 500


@ADMIN_BP.route('/logs/<int:log_id>', methods=['GET'])
@token_required
@require_admin
def get_log(user_id, log_id):
    try:
        r = RequestLog.query.get(log_id)
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error while fetching log", "details": str(e)}), 500

    if not r:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(r.to_dict())


@ADMIN_BP.route('/assignments/<int:assignment_id>/request-logs', methods=['GET'])
@token_required
@require_admin
def get_assignment_request_logs(user_id, assignment_id):
    """Return RequestLog entries related to a specific assignment (by path containing assignment_id).
    This helps admins inspect HTTP-level requests for a given assignment (including attempts POSTs).
    """
    limit = min(int(request.args.get('limit', 100)), 1000)
    offset = max(0, int(request.args.get('offset', 0)))
    try:
        pattern = f"/assignments/{assignment_id}"
        q = (RequestLog.query
             .filter(RequestLog.path.ilike(f"%{pattern}%"))
             .order_by(RequestLog.created_at.desc())
             .offset(offset)
             .limit(limit)
             .all())
        return jsonify([r.to_dict() for r in q])
    except (NoReferencedTableError, ProgrammingError) as e:
        print(f"[admin_routes] DB schema issue fetching assignment request logs: {e}")
        return jsonify({
            "data": [],
            "warning": "Database schema not initialized: RequestLog table missing.",
        }), 200
    except SQLAlchemyError as e:
        print(f"[admin_routes] SQL error fetching assignment request logs: {e}")
        return jsonify({"error": "Database error while fetching logs", "details": str(e)}), 500


# Proxy user management to auth-service (CRUD)
@ADMIN_BP.route('/users', methods=['GET'])
@token_required
@require_admin
def list_users(user_id):
    headers = {}
    auth = request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth
    r = requests.get(f"{AUTH_SERVICE}/auth/admin/users", headers=headers)
    return jsonify(r.json()), r.status_code


@ADMIN_BP.route('/users/<int:u_id>', methods=['GET'])
@token_required
@require_admin
def get_user(user_id, u_id):
    headers = {}
    auth = request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth
    r = requests.get(f"{AUTH_SERVICE}/auth/admin/users/{u_id}", headers=headers)
    return jsonify(r.json()), r.status_code


@ADMIN_BP.route('/users/<int:u_id>', methods=['PUT'])
@token_required
@require_admin
def update_user(user_id, u_id):
    payload = request.get_json(force=True)
    headers = {}
    auth = request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth
    r = requests.put(f"{AUTH_SERVICE}/auth/admin/users/{u_id}", json=payload, headers=headers)
    return jsonify(r.json()), r.status_code


@ADMIN_BP.route('/users/<int:u_id>', methods=['DELETE'])
@token_required
@require_admin
def delete_user(user_id, u_id):
    headers = {}
    auth = request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth
    r = requests.delete(f"{AUTH_SERVICE}/auth/admin/users/{u_id}", headers=headers)
    return jsonify(r.json()), r.status_code
