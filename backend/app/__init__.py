from flask import Flask
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

    db.init_app(app)
    mongo.init_app(app)

    # Swagger config
    swagger = Swagger(app)

    # Роуты
    from app.routes.auth_routes import auth_bp
    from app.routes.topics_routes import topics_bp
    from app.routes.assignments_routes import assignments_bp
    from app.routes.attempts_routes import attempts_bp
    from app.routes.attempts_history_routes import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(attempts_bp)
    app.register_blueprint(history_bp)
    
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:5173"]}},
        supports_credentials=True
    )


    return app
