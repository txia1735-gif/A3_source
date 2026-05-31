from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.profile_service import profile_service
from app.services.study_service import study_service


study_bp = Blueprint("study", __name__)


@study_bp.get("/study")
def study_page():
    users = profile_service.get_all_users()
    return render_template("study.html", users=users)


@study_bp.get("/api/study-paths")
def list_study_paths():
    user_id = request.args.get("user_id", type=int)
    return jsonify({"success": True, "data": study_service.list_study_paths(user_id)})


@study_bp.post("/api/study-paths/generate")
def generate_study_path():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    topic = payload.get("topic")
    target_days = payload.get("target_days", 7)
    if not user_id or not topic:
        return jsonify({"success": False, "message": "请提供 user_id 和 topic"}), 400

    profile = profile_service.get_profile(int(user_id))
    study_path = study_service.build_study_path(
        user_id=int(user_id),
        topic=topic,
        profile=profile,
        target_days=int(target_days),
    )
    return jsonify(
        {
            "success": True,
            "message": "学习路径已生成",
            "data": study_service.serialize_path(study_path),
        }
    )


@study_bp.patch("/api/study-paths/<int:path_id>/progress")
def update_progress(path_id: int):
    payload = request.get_json() or {}
    progress = payload.get("progress")
    if progress is None:
        return jsonify({"success": False, "message": "请提供 progress"}), 400
    return jsonify(
        {
            "success": True,
            "message": "学习进度已更新",
            "data": study_service.update_progress(path_id, float(progress)),
        }
    )

