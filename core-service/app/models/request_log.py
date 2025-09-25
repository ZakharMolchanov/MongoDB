from app import db
from datetime import datetime

class RequestLog(db.Model):
    __tablename__ = 'request_logs'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(512), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payload = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'method': self.method,
            'status_code': self.status_code,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'payload': self.payload,
        }
