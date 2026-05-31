from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import current_app

from app.extensions import cache, db
from app.models import User, UserProfile
from app.utils.profile_extract import (
    DEFAULT_DIMENSIONS,
    DEFAULT_WEIGHTS,
    apply_ebbinghaus_decay,
    build_review_suggestions,
    merge_profile_dimensions,
    parse_learning_profile,
)


class ProfileService:
    @staticmethod
    def create_or_update_user(payload: dict[str, Any]) -> User:
        username = payload["username"].strip()
        user = User.query.filter_by(username=username).first()
        if not user and payload.get("email"):
            user = User.query.filter_by(email=payload["email"].strip()).first()

        if user is None:
            user = User(
                username=username,
                email=payload["email"].strip(),
                grade=payload.get("grade"),
                major=payload.get("major"),
                bio=payload.get("bio"),
            )
            db.session.add(user)
        else:
            user.email = payload.get("email", user.email).strip()
            user.grade = payload.get("grade")
            user.major = payload.get("major")
            user.bio = payload.get("bio")

        db.session.commit()
        return user

    @staticmethod
    def build_profile(user_id: int, conversation_text: str, study_topic: str | None = None) -> UserProfile:
        user = User.query.get_or_404(user_id)
        profile = user.profile or UserProfile(
            user_id=user.id,
            dimensions=dict(DEFAULT_DIMENSIONS),
            weights=dict(DEFAULT_WEIGHTS),
        )
        if user.profile is None:
            db.session.add(profile)

        parsed = parse_learning_profile(conversation_text)
        decayed_weights = apply_ebbinghaus_decay(
            profile.weights or dict(DEFAULT_WEIGHTS),
            profile.last_updated_at,
            current_app.config["EBBINGHAUS_FACTORS"],
        )
        merged_dimensions, merged_weights = merge_profile_dimensions(
            profile.dimensions or dict(DEFAULT_DIMENSIONS),
            decayed_weights,
            parsed["dimensions"],
            parsed["weights"],
        )
        profile.dimensions = merged_dimensions
        profile.weights = merged_weights
        profile.refresh_suggestions = build_review_suggestions(merged_weights, merged_dimensions)
        profile.last_conversation = conversation_text
        profile.last_study_topic = study_topic
        profile.memory_strength = round(sum(merged_weights.values()) / max(len(merged_weights), 1), 4)
        profile.last_updated_at = datetime.utcnow()

        db.session.commit()

        cache.set_json(f"profile:{user.id}", ProfileService.serialize_profile(profile))
        current_app.logger.info("Profile updated for user_id=%s", user.id)
        return profile

    @staticmethod
    def get_profile(user_id: int) -> dict[str, Any]:
        cached = cache.get_json(f"profile:{user_id}")
        if cached:
            return cached

        user = User.query.get_or_404(user_id)
        profile = user.profile
        if profile is None:
            profile = UserProfile(
                user_id=user.id,
                dimensions=dict(DEFAULT_DIMENSIONS),
                weights=dict(DEFAULT_WEIGHTS),
                refresh_suggestions=build_review_suggestions(DEFAULT_WEIGHTS, DEFAULT_DIMENSIONS),
            )
            db.session.add(profile)
            db.session.commit()

        result = ProfileService.serialize_profile(profile)
        cache.set_json(f"profile:{user_id}", result)
        return result

    @staticmethod
    def get_all_users() -> list[dict[str, Any]]:
        users = User.query.order_by(User.created_at.desc()).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "grade": user.grade,
                "major": user.major,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]

    @staticmethod
    def serialize_profile(profile: UserProfile) -> dict[str, Any]:
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "dimensions": profile.dimensions,
            "weights": profile.weights,
            "refresh_suggestions": profile.refresh_suggestions,
            "last_conversation": profile.last_conversation,
            "last_study_topic": profile.last_study_topic,
            "memory_strength": profile.memory_strength,
            "last_updated_at": profile.last_updated_at.isoformat() if profile.last_updated_at else None,
        }


profile_service = ProfileService()

