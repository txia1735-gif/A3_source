from datetime import datetime

from app.extensions import db


class EvaluateReport(db.Model):
    __tablename__ = "evaluate_report"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    report_period = db.Column(db.String(100), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    dimension_scores = db.Column(db.JSON, nullable=False, default=dict)
    summary = db.Column(db.Text, nullable=False)
    optimization_actions = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="evaluate_reports")

