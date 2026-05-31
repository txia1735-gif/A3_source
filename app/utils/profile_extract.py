from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DEFAULT_DIMENSIONS = {
    "knowledge_base": "基础薄弱，适合从核心概念和示例入手",
    "cognitive_style": "偏好结构化、循序渐进的学习方式",
    "learning_goal": "希望建立稳定知识框架并提升应用能力",
    "weak_points": "抽象概念迁移与综合题拆解能力较弱",
    "learning_pace": "适合每日小步快跑，保持稳定节奏",
    "interest_direction": "更容易被真实案例、项目实践吸引",
    "common_errors": "易忽略边界条件、定义区分与过程复盘",
}

DEFAULT_WEIGHTS = {
    "knowledge_base": 0.75,
    "cognitive_style": 0.72,
    "learning_goal": 0.85,
    "weak_points": 0.8,
    "learning_pace": 0.7,
    "interest_direction": 0.74,
    "common_errors": 0.78,
}

KEYWORD_RULES = {
    "基础": ("knowledge_base", "当前知识基础需要先夯实基本概念、术语和常见题型"),
    "刷题": ("learning_goal", "短期目标偏向通过大量练习提升解题速度和准确率"),
    "项目": ("interest_direction", "对项目实战和落地案例兴趣较高，适合任务驱动学习"),
    "视频": ("cognitive_style", "对视频、分步骤讲解更敏感，适合可视化内容"),
    "图": ("cognitive_style", "偏好图解、结构图和思维导图辅助理解"),
    "记不住": ("weak_points", "存在记忆保持困难，需要更频繁的复习与提炼"),
    "容易错": ("common_errors", "需要记录高频易错点并在练习前先预警"),
    "考试": ("learning_goal", "学习目标偏向应试提分，需要强化重点与节奏控制"),
    "节奏慢": ("learning_pace", "学习节奏偏慢，适合拆成更小颗粒度任务"),
}


def parse_learning_profile(text: str) -> dict[str, Any]:
    dimensions = dict(DEFAULT_DIMENSIONS)
    weights = dict(DEFAULT_WEIGHTS)

    cleaned_text = text.strip()
    if not cleaned_text:
        return {"dimensions": dimensions, "weights": weights, "insights": []}

    insights: list[str] = []
    for keyword, (dimension, description) in KEYWORD_RULES.items():
        if keyword in cleaned_text:
            dimensions[dimension] = description
            weights[dimension] = min(0.98, weights.get(dimension, 0.7) + 0.08)
            insights.append(f"识别到关键词“{keyword}”，已强化{dimension}维度")

    sentence_count = max(1, len([item for item in cleaned_text.replace("。", "\n").splitlines() if item]))
    weights["learning_goal"] = min(0.99, weights["learning_goal"] + sentence_count * 0.01)

    return {"dimensions": dimensions, "weights": weights, "insights": insights}


def apply_ebbinghaus_decay(
    weights: dict[str, float],
    last_updated_at: datetime | None,
    decay_table: dict[int, float],
) -> dict[str, float]:
    if not last_updated_at:
        return weights

    now = datetime.now(timezone.utc if last_updated_at.tzinfo else None)
    days_passed = max((now - last_updated_at).days, 0)
    factor = 1.0

    for threshold, decay_factor in sorted(decay_table.items()):
        if days_passed >= threshold:
            factor = decay_factor

    return {
        key: round(max(0.18, min(value * factor, 1.0)), 4)
        for key, value in weights.items()
    }


def build_review_suggestions(weights: dict[str, float], dimensions: dict[str, str]) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    for dimension, weight in sorted(weights.items(), key=lambda item: item[1]):
        if weight <= 0.65:
            suggestions.append(
                {
                    "dimension": dimension,
                    "weight": weight,
                    "message": f"{dimension} 维度遗忘风险较高，建议优先复习：{dimensions.get(dimension, '')}",
                    "priority": "high" if weight < 0.45 else "medium",
                }
            )

    if not suggestions:
        suggestions.append(
            {
                "dimension": "overall",
                "weight": round(sum(weights.values()) / max(len(weights), 1), 4),
                "message": "当前画像保持较稳定，建议继续按照既定路径学习并做轻量复盘。",
                "priority": "low",
            }
        )
    return suggestions


def merge_profile_dimensions(
    base_dimensions: dict[str, str],
    base_weights: dict[str, float],
    new_dimensions: dict[str, str],
    new_weights: dict[str, float],
) -> tuple[dict[str, str], dict[str, float]]:
    merged_dimensions = dict(base_dimensions)
    merged_weights = dict(base_weights)

    for key, value in new_dimensions.items():
        merged_dimensions[key] = value

    for key, value in new_weights.items():
        merged_weights[key] = round(min(1.0, (merged_weights.get(key, 0.6) * 0.55) + (value * 0.45)), 4)

    return merged_dimensions, merged_weights

