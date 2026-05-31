from datetime import datetime

from app.extensions import db


class LearningResource(db.Model):
    __tablename__ = "learning_resource"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

