from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Swagger(app)

    # ✅ Подключаем только роуты аутентификации и админки
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # если ты уже добавил admin_routes.py — подключи и его
    try:
        from app.routes.admin_routes import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        pass  # если файла нет, просто пропустим

    # ✅ CORS для фронта
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

    return app
