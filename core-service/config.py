import os

class Config:
    # PostgreSQL (с настройками по умолчанию для Docker)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/mydb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB (с настройками по умолчанию для Docker)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/mongo_train")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "mongo_train")

    # Секретный ключ для сессий и токенов
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # Администраторы (переменная окружения, список админов через запятую)
    ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "admin@example.com")
