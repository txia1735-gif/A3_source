from datetime import datetime

from sqlalchemy import UniqueConstraint

from app.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    grade = db.Column(db.String(50), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    profile = db.relationship(
        "UserProfile",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )
    study_paths = db.relationship("StudyPath", back_populates="user", cascade="all, delete-orphan")
    qa_records = db.relationship("QARecord", back_populates="user", cascade="all, delete-orphan")
    evaluate_reports = db.relationship(
        "EvaluateReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(db.Model):
    __tablename__ = "user_profile"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_profile_user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    dimensions = db.Column(db.JSON, nullable=False, default=dict)
    weights = db.Column(db.JSON, nullable=False, default=dict)
    refresh_suggestions = db.Column(db.JSON, nullable=False, default=list)
    last_conversation = db.Column(db.Text, nullable=True)
    last_study_topic = db.Column(db.String(255), nullable=True)
    memory_strength = db.Column(db.Float, default=1.0, nullable=False)
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="profile")

