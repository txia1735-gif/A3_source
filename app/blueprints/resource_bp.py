from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.profile_service import profile_service
from app.services.resource_service import resource_service


resource_bp = Blueprint("resource", __name__)


@resource_bp.get("/resources")
def resource_page():
    users = profile_service.get_all_users()
    return render_template("resource.html", users=users)


@resource_bp.get("/api/resources")
def list_resources():
    user_id = request.args.get("user_id", type=int)
    return jsonify({"success": True, "data": resource_service.list_resources(user_id)})


@resource_bp.post("/api/resources/generate")
def generate_resources():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    topic = payload.get("topic")
    if not user_id or not topic:
        return jsonify({"success": False, "message": "请提供 user_id 和 topic"}), 400

    profile = profile_service.get_profile(int(user_id))
    requested_types = payload.get("resource_types")
    resources = resource_service.generate_resources(
        user_id=int(user_id),
        topic=topic,
        profile=profile,
        requested_types=requested_types,
    )
    return jsonify(
        {
            "success": True,
            "message": "学习资源已生成",
            "data": [resource_service.serialize_resource(item) for item in resources],
        }
    )

