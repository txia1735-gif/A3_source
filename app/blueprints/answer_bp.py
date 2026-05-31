from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.answer_service import answer_service
from app.services.profile_service import profile_service
from app.utils.stream_utils import build_sse_response, sse_message


answer_bp = Blueprint("answer", __name__)


@answer_bp.get("/answer")
def answer_page():
    users = profile_service.get_all_users()
    return render_template("answer.html", users=users)


@answer_bp.get("/api/answers")
def list_answers():
    user_id = request.args.get("user_id", type=int)
    return jsonify({"success": True, "data": answer_service.list_answers(user_id)})


@answer_bp.post("/api/answers")
def create_answer():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    question = payload.get("question")
    if not user_id or not question:
        return jsonify({"success": False, "message": "请提供 user_id 和 question"}), 400

    profile = profile_service.get_profile(int(user_id))
    record = answer_service.answer_question(
        user_id=int(user_id),
        question=question,
        profile=profile,
        topic=payload.get("topic"),
    )
    return jsonify(
        {
            "success": True,
            "message": "答疑完成",
            "data": answer_service.serialize_answer(record),
        }
    )


@answer_bp.get("/api/answers/stream")
def stream_answer():
    user_id = request.args.get("user_id", type=int)
    question = request.args.get("question", type=str)
    topic = request.args.get("topic", type=str)
    if not user_id or not question:
        return jsonify({"success": False, "message": "请提供 user_id 和 question"}), 400

    profile = profile_service.get_profile(user_id)

    def event_stream():
        yield sse_message("start", {"message": "开始生成回答"})
        chunks = []
        for chunk in answer_service.stream_answer(user_id, question, profile, topic):
            chunks.append(chunk)
            yield sse_message("chunk", {"content": chunk})

        record = answer_service.save_answer_record(
            user_id=user_id,
            question=question,
            answer="".join(chunks).strip(),
            topic=topic,
        )
        yield sse_message("done", answer_service.serialize_answer(record))

    return build_sse_response(event_stream())
