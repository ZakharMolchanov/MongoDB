from flask import Flask, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flasgger import Swagger
from config import Config
from flask_cors import CORS

db = SQLAlchemy()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация базы данных (PostgreSQL и MongoDB)
    db.init_app(app)
    mongo.init_app(app)

    # Swagger для авто-документации
    swagger = Swagger(app)

    # Регистрируем все роуты
    from app.routes.topics_routes import topics_bp
    from app.routes.assignments_routes import assignments_bp
    from app.routes.attempts_routes import attempts_bp
    from app.routes.attempts_history_routes import history_bp
    from app.routes.schema_routes import schema_bp   # ✅ импортируем схему
    from app.routes.admin_routes import ADMIN_BP

    # Регистрируем Blueprints
    app.register_blueprint(topics_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(attempts_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(schema_bp)
    app.register_blueprint(ADMIN_BP)

    # CORS для взаимодействия с фронтендом
    CORS(
        app,
        resources={r"/*": {"origins": [
            "http://localhost:5173",  # Vite dev
            "http://localhost",       # nginx prod
            "http://127.0.0.1"
        ]}},
        supports_credentials=True
    )

    # Request logging: сохраняем информацию о запросах для админской панели
    from app.models.request_log import RequestLog

    # For request-level logging we prefer to use a separate connection so that
    # missing tables or SQL errors do not taint the global ORM session.
    from sqlalchemy import inspect, text

    @app.after_request
    def log_request(response):
        try:
            user_id = None
            # если token_required кладёт user_id в g или в headers, попробуем взять
            from flask import g
            user_id = getattr(g, 'user_id', None)
        except Exception:
            user_id = None

        try:
            payload = None
            if request.method in ('POST', 'PUT', 'PATCH'):
                payload = request.get_data(as_text=True)
        except Exception:
            payload = None

        try:
            inspector = inspect(db.engine)
            if not inspector.has_table('request_logs'):
                # Skip logging if table not present
                return response

            params = {
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'user_id': user_id,
                'created_at': None,  # server-side default will apply
                'payload': payload,
            }
            # Insert in its own connection/transaction to avoid affecting ORM session
            conn = db.engine.connect()
            trans = conn.begin()
            try:
                # Use parameterized insert; created_at uses default if None
                insert_sql = text(
                    "INSERT INTO request_logs (path, method, status_code, user_id, created_at, payload) "
                    "VALUES (:path, :method, :status_code, :user_id, now(), :payload)"
                )
                conn.execute(insert_sql, **params)
                trans.commit()
            except Exception as e:
                try:
                    trans.rollback()
                except Exception:
                    pass
                print(f"[request_log] failed: {e}")
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        except Exception as e:
            # In case inspector or connection fails, avoid breaking the response
            print(f"[request_log] failed: {e}")
        return response

    # Return JSON for uncaught exceptions (avoid Werkzeug HTML page leaking)
    from sqlalchemy.exc import SQLAlchemyError
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(err):
        return (jsonify({"error": "Database error", "details": str(err)}), 500)

    @app.errorhandler(Exception)
    def handle_exception(err):
        # In debug mode Flask will still show debugger; in production return JSON
        return (jsonify({"error": "Internal server error", "details": str(err)}), 500)

    return app
