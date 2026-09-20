"""全局配置模块。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _as_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw not in (None, "") else default


def _as_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw not in (None, "") else default


@dataclass(frozen=True)
class AppConfig:
    """考勤系统运行参数。"""

    # 标准上下班时间（分钟，从 0 点起算）。
    start_minutes: int = field(default_factory=lambda: _as_int("AA_START_MIN", 9 * 60))       # 09:00
    end_minutes: int = field(default_factory=lambda: _as_int("AA_END_MIN", 18 * 60))          # 18:00

    # 异常阈值。
    late_grace_minutes: int = field(default_factory=lambda: _as_int("AA_LATE_GRACE", 5))      # 迟到宽限
    early_grace_minutes: int = field(default_factory=lambda: _as_int("AA_EARLY_GRACE", 5))    # 早退宽限
    overtime_hours: float = field(default_factory=lambda: _as_float("AA_OVERTIME_HOURS", 10.0))  # 加班判定时长

    # 大模型接入。
    llm_provider: str = os.getenv("AA_LLM_PROVIDER", "mock")
    llm_api_base: str = os.getenv("AA_LLM_API_BASE", "")
    llm_api_key: str = os.getenv("AA_LLM_API_KEY", "")
    llm_model: str = os.getenv("AA_LLM_MODEL", "gpt-4o-mini")

    data_dir: Path = Path(os.getenv("AA_DATA_DIR", "data"))


def load_config() -> AppConfig:
    return AppConfig()
