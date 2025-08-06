import os

class Config:
    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/mydb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "mongo_train")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
