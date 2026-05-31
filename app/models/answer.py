from datetime import datetime

from app.extensions import db


class QARecord(db.Model):
    __tablename__ = "qa_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(255), nullable=True)
    answer_type = db.Column(db.String(50), nullable=False, default="text")
    confidence = db.Column(db.Float, nullable=False, default=0.8)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="qa_records")

