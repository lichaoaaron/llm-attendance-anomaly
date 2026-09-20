"""时间处理工具。

提供时间字符串解析、分钟换算、区间重叠判断、跨天时长计算等基础能力，
供考勤清洗、班次判定、加班计算等服务复用。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


def to_minutes(hhmm: str) -> int:
    """把 'HH:MM' 或 'H:MM' 转换为从 0 点起算的分钟数。"""
    parts = hhmm.strip().split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return hours * 60 + minutes


def to_hhmm(minutes: int) -> str:
    """把分钟数格式化为 'HH:MM'（自动取模 24 小时）。"""
    minutes = minutes % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def parse_datetime(date_str: str, time_str: str) -> datetime:
    """组合日期与时间，返回 datetime 对象。"""
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def duration_minutes(start: str, end: str) -> int:
    """计算同一日内两个时间点之间的分钟差（结束早于开始则视为跨天）。"""
    s, e = to_minutes(start), to_minutes(end)
    if e < s:
        e += 24 * 60
    return e - s


def overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    """判断两个时间段是否重叠（含边界）。"""
    a_s, a_e = to_minutes(a_start), to_minutes(a_end)
    b_s, b_e = to_minutes(b_start), to_minutes(b_end)
    return a_s < b_e and b_s < a_e


@dataclass
class TimeRange:
    """一段时间区间。"""

    start: str
    end: str

    def duration(self) -> int:
        return duration_minutes(self.start, self.end)


def minutes_to_hours(minutes: int) -> float:
    """分钟转小时（保留两位小数）。"""
    return round(minutes / 60.0, 2)


def is_weekend(date_str: str) -> bool:
    """判断日期是否为周六或周日。"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.weekday() >= 5


def add_days(date_str: str, days: int) -> str:
    """日期加减天数，返回 'YYYY-MM-DD'。"""
    d = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)
    return d.strftime("%Y-%m-%d")
