from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from flask import current_app

from app.extensions import db
from app.models import LearningResource, User
from app.utils.file_utils import write_text_file


class ResourceService:
    RESOURCE_BUILDERS = {
        "course_document": "generate_course_document",
        "mind_map": "generate_mind_map",
        "quiz_bank": "generate_quiz_bank",
        "video_script": "generate_video_script",
        "code_example": "generate_code_example",
        "ppt_outline": "generate_ppt_outline",
    }

    @classmethod
    def generate_resources(
        cls,
        user_id: int,
        topic: str,
        profile: dict,
        requested_types: list[str] | None = None,
    ) -> list[LearningResource]:
        User.query.get_or_404(user_id)
        resource_types = requested_types or current_app.config["RESOURCE_TYPES"]
        created_resources: list[LearningResource] = []

        for resource_type in resource_types:
            method_name = cls.RESOURCE_BUILDERS.get(resource_type)
            if not method_name:
                continue
            builder = getattr(cls, method_name)
            title, description, content, metadata = builder(topic, profile)

            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}_{resource_type}.md"
            output_path = Path(current_app.config["GENERATED_FOLDER"]) / filename
            write_text_file(output_path, content)

            resource = LearningResource(
                user_id=user_id,
                title=title,
                topic=topic,
                resource_type=resource_type,
                description=description,
                content=content,
                metadata_json=metadata,
                file_path=str(output_path),
            )
            db.session.add(resource)
            created_resources.append(resource)

        db.session.commit()
        current_app.logger.info(
            "Generated %s resources for user_id=%s topic=%s",
            len(created_resources),
            user_id,
            topic,
        )
        return created_resources

    @staticmethod
    def list_resources(user_id: int | None = None) -> list[dict]:
        query = LearningResource.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        resources = query.order_by(LearningResource.created_at.desc()).all()
        return [ResourceService.serialize_resource(item) for item in resources]

    @staticmethod
    def serialize_resource(resource: LearningResource) -> dict:
        return {
            "id": resource.id,
            "user_id": resource.user_id,
            "title": resource.title,
            "topic": resource.topic,
            "resource_type": resource.resource_type,
            "description": resource.description,
            "content": resource.content,
            "metadata": resource.metadata_json,
            "file_path": resource.file_path,
            "created_at": resource.created_at.isoformat(),
        }

    @staticmethod
    def generate_course_document(topic: str, profile: dict):
        goal = profile["dimensions"].get("learning_goal", "")
        content = f"""# {topic} 课程讲解文档

## 学习目标
- {goal}
- 建立从概念到应用的完整认知链路

## 核心知识拆解
1. 概念定义与场景背景
2. 关键原理与典型流程
3. 常见题型和项目化应用

## 针对性建议
- 先看例子再抽象总结
- 每节结束后做 3 分钟复盘
- 把易错点写成个人检查单

## 课后行动
- 今天完成一轮概念整理
- 明天完成配套练习
- 第三天做一次回顾测验
"""
        return (
            f"{topic} 课程讲解文档",
            "面向当前学习画像生成的结构化讲义文档",
            content,
            {"format": "markdown", "audience": "student"},
        )

    @staticmethod
    def generate_mind_map(topic: str, profile: dict):
        weak_points = profile["dimensions"].get("weak_points", "")
        content = f"""# {topic} 思维导图

```mermaid
mindmap
  root(({topic}))
    概念基础
      定义
      术语
    原理机制
      输入
      处理
      输出
    应用场景
      题目分析
      项目实践
    风险提醒
      {weak_points}
```
"""
        return (
            f"{topic} 思维导图",
            "帮助学生快速形成结构化知识网络",
            content,
            {"format": "mermaid"},
        )

    @staticmethod
    def generate_quiz_bank(topic: str, profile: dict):
        common_errors = profile["dimensions"].get("common_errors", "")
        content = f"""# {topic} 练习题题库

## 选择题
1. 请解释 {topic} 的核心定义并区分常见误区。
2. 在真实应用中，{topic} 最关键的步骤是什么？

## 简答题
1. 请用自己的话描述 {topic} 的完整流程。
2. 针对以下易错点，应该如何避免：{common_errors}

## 提升题
1. 设计一个与 {topic} 相关的小项目或实验方案。
"""
        return (
            f"{topic} 练习题题库",
            "包含基础题、简答题和提升题的练习集合",
            content,
            {"format": "markdown", "question_count": 5},
        )

    @staticmethod
    def generate_video_script(topic: str, profile: dict):
        style = profile["dimensions"].get("cognitive_style", "")
        content = f"""# {topic} 教学视频脚本

## 片头
- 引入问题：为什么要学习 {topic}？
- 场景共鸣：把抽象知识放进真实案例里

## 正片结构
1. 1 分钟讲清概念
2. 2 分钟拆解流程
3. 2 分钟结合例题/项目说明
4. 1 分钟总结易错点与复习建议

## 表达风格
- {style}
- 多使用对比图和步骤动画
"""
        return (
            f"{topic} 教学视频脚本",
            "可直接用于录制视频或动画讲解的脚本",
            content,
            {"format": "script", "estimated_minutes": 6},
        )

    @staticmethod
    def generate_code_example(topic: str, profile: dict):
        safe_name = re.sub(r"[^0-9a-zA-Z_]+", "_", topic.strip().lower())
        safe_name = safe_name.strip("_") or "learning_topic"
        if safe_name[0].isdigit():
            safe_name = f"topic_{safe_name}"
        content = f"""# {topic} 代码实操案例

```python
def explain_{safe_name}():
    steps = [
        "理解输入条件",
        "拆分处理流程",
        "验证输出结果",
        "复盘易错边界",
    ]
    for index, step in enumerate(steps, start=1):
        print(f"步骤{{index}}: {{step}}")


if __name__ == "__main__":
    explain_{safe_name}()
```

## 实操说明
- 先运行示例理解主流程
- 再尝试修改输入验证边界情况
- 最后把逻辑封装成自己的版本
"""
        return (
            f"{topic} 代码实操案例",
            "结合主题生成的可运行示例代码",
            content,
            {"format": "python"},
        )

    @staticmethod
    def generate_ppt_outline(topic: str, profile: dict):
        pace = profile["dimensions"].get("learning_pace", "")
        content = f"""# {topic} PPT 课件提纲

1. 封面：主题与学习目标
2. 背景：为什么这个知识点重要
3. 核心概念：定义与关键词
4. 原理流程：图示化说明
5. 应用案例：题目或项目落地
6. 易错点：重点预警
7. 复习计划：{pace}
"""
        return (
            f"{topic} PPT 课件提纲",
            "适合继续加工为演示课件的 PPT 大纲",
            content,
            {"format": "ppt-outline", "slides": 7},
        )


resource_service = ResourceService()
