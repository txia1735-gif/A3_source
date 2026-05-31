from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.profile_service import profile_service


user_bp = Blueprint("user", __name__)


@user_bp.get("/")
def index():
    users = profile_service.get_all_users()
    return render_template("index.html", users=users)


@user_bp.get("/profile")
def profile_page():
    users = profile_service.get_all_users()
    return render_template("profile.html", users=users)


@user_bp.get("/api/users")
def list_users():
    return jsonify({"success": True, "data": profile_service.get_all_users()})


@user_bp.post("/api/users")
def create_user():
    payload = request.get_json() or {}
    required_fields = ["username", "email"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return (
            jsonify({"success": False, "message": f"缺少必要字段: {', '.join(missing)}"}),
            400,
        )

    user = profile_service.create_or_update_user(payload)
    return jsonify(
        {
            "success": True,
            "message": "用户信息已保存",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "grade": user.grade,
                "major": user.major,
                "bio": user.bio,
            },
        }
    )


@user_bp.post("/api/profile/build")
def build_profile():
    payload = request.get_json() or {}
    if not payload.get("user_id") or not payload.get("conversation_text"):
        return jsonify({"success": False, "message": "请提供 user_id 和 conversation_text"}), 400

    profile = profile_service.build_profile(
        user_id=int(payload["user_id"]),
        conversation_text=payload["conversation_text"],
        study_topic=payload.get("study_topic"),
    )
    return jsonify(
        {
            "success": True,
            "message": "学习画像已更新",
            "data": profile_service.serialize_profile(profile),
        }
    )


@user_bp.get("/api/profile/<int:user_id>")
def get_profile(user_id: int):
    return jsonify({"success": True, "data": profile_service.get_profile(user_id)})

