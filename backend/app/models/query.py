from app import db
from datetime import datetime

class Query(db.Model):
    __tablename__ = "queries"

    query_id = db.Column(db.Integer, primary_key=True)

    # FK на users.id (без дубликатов)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    assignment_id = db.Column(db.Integer,
                              db.ForeignKey("assignments.assignment_id"),
                              nullable=False)

    query_text = db.Column(db.Text, nullable=False)   # исходный запрос (JSON-строка)
    status = db.Column(db.String(50), nullable=False) # ok / failed / error

    # лучше JSON (в PG это JSONB)
    result = db.Column(db.JSON)                       # нормализованный результат
    error_message = db.Column(db.Text)                # текст ошибки
    error_json = db.Column(db.JSON)                   # структурированная ошибка (опц.)

    # метрики
    exec_ms = db.Column(db.Integer)                   # время выполнения в мс
    result_count = db.Column(db.Integer)              # кол-во документов в результате

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignment = db.relationship("Assignment", backref=db.backref("queries", lazy=True))
