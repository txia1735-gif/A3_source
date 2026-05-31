from __future__ import annotations

from statistics import mean

from flask import current_app

from app.extensions import db
from app.models import EvaluateReport, QARecord, StudyPath, User


class EvaluateService:
    @staticmethod
    def generate_report(user_id: int, profile: dict) -> EvaluateReport:
        User.query.get_or_404(user_id)
        answers = QARecord.query.filter_by(user_id=user_id).all()
        paths = StudyPath.query.filter_by(user_id=user_id).all()

        answer_accuracy = round(min(100.0, 68.0 + len(answers) * 4.5), 2)
        profile_match = round(profile.get("memory_strength", 0.75) * 100, 2)
        resource_usage = round(min(100.0, 55.0 + len(paths) * 8.0), 2)
        forgetting_recovery = round(
            min(100.0, mean(list(profile["weights"].values())) * 100 + len(answers) * 1.8),
            2,
        )

        dimension_scores = {
            "answer_accuracy": answer_accuracy,
            "profile_match": profile_match,
            "resource_usage": resource_usage,
            "forgetting_recovery": forgetting_recovery,
        }
        overall_score = round(mean(dimension_scores.values()), 2)

        summary = (
            f"当前综合得分为 {overall_score} 分。画像匹配度表现稳定，说明个性化策略基本有效；"
            f"答题正确率与遗忘恢复率仍有继续提升空间，建议结合错题复盘和 1/3/7 天复习安排。"
        )
        actions = [
            "将第 1 天和第 3 天的复习任务设为必做提醒",
            "对低权重维度增加图解和短练习的组合资源",
            "在每个学习单元结束后追加 3 题即时测验",
            "每周生成一次评估报告，动态修正学习路径",
        ]

        report = EvaluateReport(
            user_id=user_id,
            title="学习效果评估报告",
            report_period="近 7 天",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            summary=summary,
            optimization_actions=actions,
        )
        db.session.add(report)
        db.session.commit()
        current_app.logger.info("Evaluation report created for user_id=%s", user_id)
        return report

    @staticmethod
    def list_reports(user_id: int | None = None) -> list[dict]:
        query = EvaluateReport.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        reports = query.order_by(EvaluateReport.created_at.desc()).all()
        return [EvaluateService.serialize_report(item) for item in reports]

    @staticmethod
    def serialize_report(report: EvaluateReport) -> dict:
        return {
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "report_period": report.report_period,
            "overall_score": report.overall_score,
            "dimension_scores": report.dimension_scores,
            "summary": report.summary,
            "optimization_actions": report.optimization_actions,
            "created_at": report.created_at.isoformat(),
        }


evaluate_service = EvaluateService()

