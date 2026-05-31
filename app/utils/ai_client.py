from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import requests


@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    raw: dict | None = None


class AIClient:
    def __init__(self, app=None) -> None:
        self.logger = logging.getLogger(__name__)
        self.app = app

    def init_app(self, app) -> None:
        self.app = app

    @property
    def provider(self) -> str:
        if not self.app:
            return "mock"
        return self.app.config.get("AI_PROVIDER", "mock")

    def complete(self, system_prompt: str, user_prompt: str) -> AIResponse:
        if self.provider == "openai" and self.app and self.app.config.get("OPENAI_API_KEY"):
            return self._openai_complete(system_prompt, user_prompt)
        return self._mock_complete(system_prompt, user_prompt)

    def stream(self, system_prompt: str, user_prompt: str) -> Iterable[str]:
        response = self.complete(system_prompt, user_prompt)
        for line in response.content.splitlines():
            yield line + "\n"

    def _mock_complete(self, system_prompt: str, user_prompt: str) -> AIResponse:
        short_system = system_prompt[:80].strip()
        content = (
            "这是一个本地模拟 AI 结果，用于在未接入真实模型时完整演示系统流程。\n\n"
            f"系统角色摘要：{short_system}\n"
            f"用户需求：{user_prompt.strip()}\n\n"
            "建议输出：\n"
            "1. 先提炼学习目标与知识短板。\n"
            "2. 再生成结构化学习资源与路径。\n"
            "3. 最后根据复习周期安排阶段检查。"
        )
        return AIResponse(content=content, provider="mock", model="mock-educator")

    def _openai_complete(self, system_prompt: str, user_prompt: str) -> AIResponse:
        base_url = self.app.config["OPENAI_BASE_URL"].rstrip("/")
        api_key = self.app.config["OPENAI_API_KEY"]
        model = self.app.config["OPENAI_MODEL"]
        timeout = self.app.config["AI_REQUEST_TIMEOUT"]

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return AIResponse(content=content, provider="openai", model=model, raw=data)


ai_client = AIClient()

