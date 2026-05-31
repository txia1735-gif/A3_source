from datetime import datetime

from app.extensions import db


class StudyPath(db.Model):
    __tablename__ = "study_path"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    target_days = db.Column(db.Integer, nullable=False, default=7)
    status = db.Column(db.String(30), nullable=False, default="active")
    path_nodes = db.Column(db.JSON, nullable=False, default=list)
    recommendations = db.Column(db.JSON, nullable=False, default=list)
    progress = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship("User", back_populates="study_paths")

