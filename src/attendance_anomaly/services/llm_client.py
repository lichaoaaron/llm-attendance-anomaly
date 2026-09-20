"""大模型客户端抽象。

用于为识别出的考勤异常生成自然语言解释，帮助 HR 快速理解异常背景。
默认使用规则模板离线生成，可切换为真实大模型。
"""
from __future__ import annotations

import json
import urllib.request
from abc import ABC, abstractmethod

from attendance_anomaly.models.attendance import Anomaly

_TYPE_LABEL = {
    "late": "迟到",
    "early_leave": "早退",
    "missing_punch": "缺卡",
    "overtime": "加班",
}


class LLMClient(ABC):
    """大模型客户端统一接口。"""

    @abstractmethod
    def explain(self, anomaly: Anomaly) -> str:
        """为一条异常生成自然语言解释。"""


class MockLLMClient(LLMClient):
    """规则模板客户端：离线生成解释。"""

    def explain(self, anomaly: Anomaly) -> str:
        label = _TYPE_LABEL.get(anomaly.anomaly_type, anomaly.anomaly_type)
        return f"{anomaly.date} 员工 {anomaly.employee_id} 发生「{label}」异常，详情：{anomaly.detail}"


class OpenAICompatibleClient(LLMClient):
    """OpenAI 兼容接口客户端。"""

    def __init__(self, api_base: str, api_key: str, model: str) -> None:
        if not api_base or not api_key:
            raise ValueError("api_base 与 api_key 不能为空")
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model

    def explain(self, anomaly: Anomaly) -> str:
        label = _TYPE_LABEL.get(anomaly.anomaly_type, anomaly.anomaly_type)
        url = f"{self.api_base}/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是考勤助理，用一句话解释考勤异常。"},
                    {
                        "role": "user",
                        "content": f"员工 {anomaly.employee_id} 于 {anomaly.date} 发生「{label}」：{anomaly.detail}",
                    },
                ],
                "temperature": 0.3,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()
