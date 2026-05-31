from __future__ import annotations

from flask import current_app

from app.services.answer_service import answer_service
from app.services.evaluate_service import evaluate_service
from app.services.profile_service import profile_service
from app.services.resource_service import resource_service
from app.services.study_service import study_service


class AgentService:
    AGENTS = [
        "profile_agent",
        "knowledge_agent",
        "resource_agent",
        "path_agent",
        "qa_agent",
        "evaluation_agent",
    ]

    @staticmethod
    def orchestrate_learning_flow(
        user_id: int,
        conversation_text: str,
        topic: str,
        include_answer: bool = True,
    ) -> dict:
        current_app.logger.info(
            "Agent orchestration started for user_id=%s topic=%s", user_id, topic
        )

        profile = profile_service.build_profile(user_id, conversation_text, topic)
        serialized_profile = profile_service.serialize_profile(profile)

        resources = resource_service.generate_resources(
            user_id=user_id,
            topic=topic,
            profile=serialized_profile,
        )
        study_path = study_service.build_study_path(
            user_id=user_id,
            topic=topic,
            profile=serialized_profile,
            target_days=7,
        )
        answer_record = None
        if include_answer:
            answer_record = answer_service.answer_question(
                user_id=user_id,
                question=f"请用适合我的方式快速理解 {topic}",
                profile=serialized_profile,
                topic=topic,
            )
        report = evaluate_service.generate_report(user_id=user_id, profile=serialized_profile)

        current_app.logger.info(
            "Agent orchestration completed for user_id=%s topic=%s", user_id, topic
        )
        return {
            "agents": AgentService.AGENTS,
            "profile": serialized_profile,
            "resources": [resource_service.serialize_resource(item) for item in resources],
            "study_path": study_service.serialize_path(study_path),
            "answer": answer_service.serialize_answer(answer_record) if answer_record else None,
            "report": evaluate_service.serialize_report(report),
        }


agent_service = AgentService()

