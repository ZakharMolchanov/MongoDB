from app import db
from datetime import datetime

class CompletedAssignment(db.Model):
    __tablename__ = "completed_assignments"

    completed_assignment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.assignment_id"), nullable=False)
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)

    # не обязательно, но удобно для ORM-навигации
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assignment = db.relationship("Assignment", backref=db.backref("completed_by", lazy=True))
