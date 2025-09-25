from app import db
import json

class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # новое поле
    schema_json = db.Column(db.JSON)

    @property
    def required_method(self):
        try:
            if not self.schema_json:
                return None
            if isinstance(self.schema_json, dict):
                return self.schema_json.get('required_method')
            try:
                conf = json.loads(self.schema_json)
                return conf.get('required_method')
            except Exception:
                return None
        except Exception:
            return None

    tests = db.relationship("AssignmentTest", backref="assignment", cascade="all, delete-orphan")
