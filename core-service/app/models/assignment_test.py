from app import db
from datetime import datetime

class AssignmentTest(db.Model):
    __tablename__ = "assignment_tests"

    test_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.assignment_id"), nullable=False)
    expected_result = db.Column(db.JSON, nullable=False)  # было Text
    test_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
