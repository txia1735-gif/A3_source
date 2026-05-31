from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.evaluate_service import evaluate_service
from app.services.profile_service import profile_service


evaluate_bp = Blueprint("evaluate", __name__)


@evaluate_bp.get("/evaluate")
def evaluate_page():
    users = profile_service.get_all_users()
    return render_template("evaluate.html", users=users)


@evaluate_bp.get("/api/evaluations")
def list_reports():
    user_id = request.args.get("user_id", type=int)
    return jsonify({"success": True, "data": evaluate_service.list_reports(user_id)})


@evaluate_bp.post("/api/evaluations/generate")
def generate_report():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "请提供 user_id"}), 400

    profile = profile_service.get_profile(int(user_id))
    report = evaluate_service.generate_report(int(user_id), profile)
    return jsonify(
        {
            "success": True,
            "message": "评估报告已生成",
            "data": evaluate_service.serialize_report(report),
        }
    )

