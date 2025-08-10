from app import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tests = db.relationship("AssignmentTest", backref="assignment", lazy=True, cascade="all,delete")