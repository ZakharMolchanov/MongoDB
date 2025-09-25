from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.user import User
from app.utils.auth import hash_password, verify_password, generate_access_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
  data = request.json or {}
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
    password_hash=hash_password(password),
  )

  admin_emails = {e.strip().lower() for e in current_app.config.get('ADMIN_EMAILS', '').split(',') if e.strip()}
  if (email or '').lower() in admin_emails:
    new_user.is_admin = True

  db.session.add(new_user)
  db.session.commit()

  return jsonify({"message": "User registered"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
  data = request.json or {}
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
    "created_at": user.created_at.isoformat(),
    "is_admin": bool(getattr(user, 'is_admin', False)),
  })


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_profile(user_id):
  data = request.json or {}
  email = data.get("email")
  first_name = data.get("first_name")
  last_name = data.get("last_name")
  password = data.get("password")

  user = User.query.get(user_id)
  if not user:
    return jsonify({"error": "User not found"}), 404

  if email and email != user.email:
    if User.query.filter_by(email=email).first():
      return jsonify({"error": "Email already taken"}), 400
    user.email = email

  if first_name:
    user.first_name = first_name
  if last_name:
    user.last_name = last_name
  if password:
    user.password_hash = hash_password(password)

  db.session.commit()

  return jsonify({
    "message": "Profile updated",
    "user": {
      "id": user.id,
      "email": user.email,
      "first_name": user.first_name,
      "last_name": user.last_name,
    },
  })


@auth_bp.route("/me", methods=["DELETE"])
@token_required
def delete_account(user_id):
  user = User.query.get(user_id)
  if not user:
    return jsonify({"error": "User not found"}), 404

  db.session.delete(user)
  db.session.commit()

  return jsonify({"message": "Account deleted"})


@auth_bp.route("/is-admin/<int:user_id>", methods=["GET"])
@token_required
def check_is_admin(request_user_id, user_id):
  user = User.query.get(user_id)
  if not user:
    return jsonify({"is_admin": False, "error": "User not found"}), 404

  if getattr(user, 'is_admin', False):
    return jsonify({"is_admin": True})

  admin_emails = {e.strip().lower() for e in current_app.config.get("ADMIN_EMAILS", "").split(",") if e.strip()}
  is_admin = (user.email or "").lower() in admin_emails

  return jsonify({"is_admin": is_admin})


@auth_bp.route('/admin/users', methods=['GET'])
@token_required
def admin_list_users(current_user_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  users = User.query.order_by(User.id.asc()).all()
  return jsonify([{
    'id': u.id,
    'email': u.email,
    'first_name': u.first_name,
    'last_name': u.last_name,
    'created_at': u.created_at.isoformat(),
    'is_admin': bool(getattr(u, 'is_admin', False)),
  } for u in users])


@auth_bp.route('/admin/users/<int:u_id>', methods=['GET'])
@token_required
def admin_get_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  return jsonify({
    'id': u.id,
    'email': u.email,
    'first_name': u.first_name,
    'last_name': u.last_name,
    'created_at': u.created_at.isoformat(),
    'is_admin': bool(getattr(u, 'is_admin', False)),
  })


@auth_bp.route('/admin/users/<int:u_id>', methods=['PUT'])
@token_required
def admin_update_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  data = request.get_json(force=True) or {}
  if 'email' in data and data['email']:
    if User.query.filter(User.email == data['email'], User.id != u_id).first():
      return jsonify({'error': 'Email already taken'}), 400
    u.email = data['email']
  if 'first_name' in data:
    u.first_name = data['first_name']
  if 'last_name' in data:
    u.last_name = data['last_name']
  if 'is_admin' in data:
    u.is_admin = bool(data['is_admin'])
  db.session.commit()
  return jsonify({'message': 'User updated'})


@auth_bp.route('/admin/users/<int:u_id>', methods=['DELETE'])
@token_required
def admin_delete_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  db.session.delete(u)
  db.session.commit()
  return jsonify({'message': 'User deleted'})
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.user import User
from app.utils.auth import hash_password, verify_password, generate_access_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - first_name
            - last_name
            - password
          properties:
            email:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            password:
              type: string
    responses:
      201:
        description: Пользователь успешно зарегистрирован
      400:
        description: Ошибка валидации
    """
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

    # назначаем админа если email в списке ADMIN_EMAILS
    admin_emails = {e.strip().lower() for e in current_app.config.get('ADMIN_EMAILS','').split(',') if e.strip()}
    if (email or '').lower() in admin_emails:
      new_user.is_admin = True

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Вход пользователя
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Успешная аутентификация
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Неверные учетные данные
    """
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
    """
    Получить профиль текущего пользователя
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: Профиль пользователя
      404:
        description: Пользователь не найден
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
  "created_at": user.created_at.isoformat(),
  "is_admin": bool(user.is_admin)
    })


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_profile(user_id):
    """
    Обновить профиль пользователя
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            email:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            password:
              type: string
    responses:
      200:
        description: Профиль обновлён
      400:
        description: Email уже занят
      404:
        description: Пользователь не найден
    """
    data = request.json
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already taken"}), 400
        user.email = email

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if password:
        user.password_hash = hash_password(password)

    db.session.commit()

    return jsonify({
        "message": "Profile updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    })


@auth_bp.route("/me", methods=["DELETE"])
@token_required
def delete_account(user_id):
    """
    Удалить аккаунт текущего пользователя
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: Аккаунт удалён
      404:
        description: Пользователь не найден
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted"})
@auth_bp.route("/is-admin/<int:user_id>", methods=["GET"])
@token_required
def check_is_admin(request_user_id, user_id):
    """
    Проверка, является ли пользователь админом
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
    responses:
      200:
        description: Флаг админа
        schema:
          type: object
          properties:
            is_admin:
              type: boolean
    """
    user = User.query.get(user_id)
    if not user:
      return jsonify({"is_admin": False, "error": "User not found"}), 404

    # если в БД есть флаг is_admin — используем его
    if hasattr(user, 'is_admin') and user.is_admin:
      return jsonify({"is_admin": True})

    # иначе читаем список админов из переменной окружения ADMIN_EMAILS
    admin_emails = {e.strip().lower() for e in current_app.config.get("ADMIN_EMAILS", "").split(",") if e.strip()}
    is_admin = (user.email or "").lower() in admin_emails

    return jsonify({"is_admin": is_admin})


@auth_bp.route('/admin/users', methods=['GET'])
@token_required
def admin_list_users(current_user_id):
  # только админы
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  users = User.query.order_by(User.id.asc()).all()
  return jsonify([{
    'id': u.id,
    'email': u.email,
    'first_name': u.first_name,
    'last_name': u.last_name,
    'created_at': u.created_at.isoformat(),
    'is_admin': bool(getattr(u, 'is_admin', False))
  } for u in users])


@auth_bp.route('/admin/users/<int:u_id>', methods=['GET'])
@token_required
def admin_get_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  return jsonify({
    'id': u.id,
    'email': u.email,
    'first_name': u.first_name,
    'last_name': u.last_name,
    'created_at': u.created_at.isoformat(),
    'is_admin': bool(getattr(u, 'is_admin', False))
  })


@auth_bp.route('/admin/users/<int:u_id>', methods=['PUT'])
@token_required
def admin_update_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  data = request.get_json(force=True)
  if 'email' in data and data['email']:
    if User.query.filter(User.email==data['email'], User.id!=u_id).first():
      return jsonify({'error': 'Email already taken'}), 400
    u.email = data['email']
  if 'first_name' in data:
    u.first_name = data['first_name']
  if 'last_name' in data:
    u.last_name = data['last_name']
  if 'is_admin' in data:
    u.is_admin = bool(data['is_admin'])
  db.session.commit()
  return jsonify({'message': 'User updated'})


@auth_bp.route('/admin/users/<int:u_id>', methods=['DELETE'])
@token_required
def admin_delete_user(current_user_id, u_id):
  current = User.query.get(current_user_id)
  if not current or not getattr(current, 'is_admin', False):
    return jsonify({'error': 'Admin only'}), 403
  u = User.query.get(u_id)
  if not u:
    return jsonify({'error': 'Not found'}), 404
  db.session.delete(u)
  db.session.commit()
  return jsonify({'message': 'User deleted'})
  db.session.commit()
  return jsonify({'message': 'User deleted'})