"""加班申请数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class OvertimeRequest:
    """一条加班申请。"""

    request_id: str
    employee_id: str
    date: str
    hours: float
    reason: str = ""
    status: str = "approved"   # pending / approved / rejected
    compensated: bool = False  # 是否已调休

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "employee_id": self.employee_id,
            "date": self.date,
            "hours": self.hours,
            "reason": self.reason,
            "status": self.status,
            "compensated": self.compensated,
        }


@dataclass
class OvertimeSummary:
    """员工加班汇总。"""

    employee_id: str
    total_hours: float
    request_count: int
    compensated_hours: float
    remaining_hours: float

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "total_hours": round(self.total_hours, 2),
            "request_count": self.request_count,
            "compensated_hours": round(self.compensated_hours, 2),
            "remaining_hours": round(self.remaining_hours, 2),
        }
