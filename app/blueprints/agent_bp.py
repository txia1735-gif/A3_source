from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.agent_service import agent_service


agent_bp = Blueprint("agent", __name__)


@agent_bp.post("/api/agents/orchestrate")
def orchestrate():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    conversation_text = payload.get("conversation_text")
    topic = payload.get("topic")
    if not user_id or not conversation_text or not topic:
        return (
            jsonify({"success": False, "message": "请提供 user_id、conversation_text、topic"}),
            400,
        )

    result = agent_service.orchestrate_learning_flow(
        user_id=int(user_id),
        conversation_text=conversation_text,
        topic=topic,
        include_answer=payload.get("include_answer", True),
    )
    return jsonify({"success": True, "message": "多智能体协同完成", "data": result})

