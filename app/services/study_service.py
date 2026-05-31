from __future__ import annotations

from datetime import datetime, timedelta

from flask import current_app

from app.extensions import db
from app.models import StudyPath, User


class StudyService:
    @staticmethod
    def build_study_path(user_id: int, topic: str, profile: dict, target_days: int = 7) -> StudyPath:
        User.query.get_or_404(user_id)
        weak_points = profile["dimensions"].get("weak_points", "")
        common_errors = profile["dimensions"].get("common_errors", "")
        review_suggestions = profile.get("refresh_suggestions", [])

        path_nodes = []
        today = datetime.utcnow()
        for day in range(target_days):
            stage = "学习新知识" if day < 3 else "强化应用" if day < 5 else "复习巩固"
            focus = (
                "核心概念理解"
                if day == 0
                else "例题训练"
                if day in (1, 2)
                else "综合练习"
                if day in (3, 4)
                else "遗忘恢复与查漏补缺"
            )
            path_nodes.append(
                {
                    "day": day + 1,
                    "date": (today + timedelta(days=day)).date().isoformat(),
                    "stage": stage,
                    "focus": focus,
                    "task": f"围绕 {topic} 完成 {focus}，同步关注：{weak_points}",
                    "review_tip": review_suggestions[min(day, len(review_suggestions) - 1)]["message"]
                    if review_suggestions
                    else "保持轻量复盘",
                }
            )

        recommendations = [
            f"优先处理短板：{weak_points}",
            f"练习时重点自查：{common_errors}",
            "每次学习结束后输出 3 条关键结论",
            "在第 1/3/7 天设置复习提醒，对抗遗忘曲线",
        ]

        study_path = StudyPath(
            user_id=user_id,
            topic=topic,
            target_days=target_days,
            path_nodes=path_nodes,
            recommendations=recommendations,
            progress=0.0,
        )
        db.session.add(study_path)
        db.session.commit()
        current_app.logger.info("Study path created for user_id=%s topic=%s", user_id, topic)
        return study_path

    @staticmethod
    def list_study_paths(user_id: int | None = None) -> list[dict]:
        query = StudyPath.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        items = query.order_by(StudyPath.created_at.desc()).all()
        return [StudyService.serialize_path(item) for item in items]

    @staticmethod
    def update_progress(path_id: int, progress: float) -> dict:
        study_path = StudyPath.query.get_or_404(path_id)
        study_path.progress = max(0.0, min(progress, 100.0))
        study_path.status = "completed" if study_path.progress >= 100 else "active"
        db.session.commit()
        return StudyService.serialize_path(study_path)

    @staticmethod
    def serialize_path(study_path: StudyPath) -> dict:
        return {
            "id": study_path.id,
            "user_id": study_path.user_id,
            "topic": study_path.topic,
            "target_days": study_path.target_days,
            "status": study_path.status,
            "path_nodes": study_path.path_nodes,
            "recommendations": study_path.recommendations,
            "progress": study_path.progress,
            "created_at": study_path.created_at.isoformat(),
            "updated_at": study_path.updated_at.isoformat(),
        }


study_service = StudyService()

