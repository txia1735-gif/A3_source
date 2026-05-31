from __future__ import annotations

from typing import Iterable

from flask import current_app

from app.extensions import db
from app.models import QARecord, User
from app.utils.ai_client import ai_client


class AnswerService:
    SYSTEM_PROMPT = (
        "你是一名耐心、结构清晰的学习辅导智能体。请结合学生画像，用通俗语言解答问题，"
        "先给核心结论，再给步骤说明，最后补充易错提醒和下一步建议。"
    )

    @staticmethod
    def answer_question(user_id: int, question: str, profile: dict, topic: str | None = None) -> QARecord:
        User.query.get_or_404(user_id)
        user_prompt = (
            f"学习画像：{profile['dimensions']}\n"
            f"画像权重：{profile['weights']}\n"
            f"提问主题：{topic or '未指定'}\n"
            f"学生问题：{question}"
        )
        ai_client.init_app(current_app)
        result = ai_client.complete(AnswerService.SYSTEM_PROMPT, user_prompt)
        return AnswerService.save_answer_record(
            user_id=user_id,
            question=question,
            answer=result.content,
            topic=topic,
            provider=result.provider,
            model=result.model,
            confidence=0.86 if result.provider == "mock" else 0.92,
        )

    @staticmethod
    def save_answer_record(
        user_id: int,
        question: str,
        answer: str,
        topic: str | None = None,
        provider: str = "mock",
        model: str = "mock-educator",
        confidence: float = 0.86,
    ) -> QARecord:
        User.query.get_or_404(user_id)

        record = QARecord(
            user_id=user_id,
            question=question,
            answer=answer,
            topic=topic,
            answer_type="text",
            confidence=confidence,
            metadata_json={"provider": provider, "model": model},
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def stream_answer(user_id: int, question: str, profile: dict, topic: str | None = None) -> Iterable[str]:
        User.query.get_or_404(user_id)
        user_prompt = (
            f"学习画像：{profile['dimensions']}\n"
            f"提问主题：{topic or '未指定'}\n"
            f"学生问题：{question}"
        )
        ai_client.init_app(current_app)
        for chunk in ai_client.stream(AnswerService.SYSTEM_PROMPT, user_prompt):
            yield chunk

    @staticmethod
    def list_answers(user_id: int | None = None) -> list[dict]:
        query = QARecord.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        answers = query.order_by(QARecord.created_at.desc()).all()
        return [AnswerService.serialize_answer(item) for item in answers]

    @staticmethod
    def serialize_answer(record: QARecord) -> dict:
        return {
            "id": record.id,
            "user_id": record.user_id,
            "question": record.question,
            "answer": record.answer,
            "topic": record.topic,
            "answer_type": record.answer_type,
            "confidence": record.confidence,
            "metadata": record.metadata_json,
            "created_at": record.created_at.isoformat(),
        }


answer_service = AnswerService()
