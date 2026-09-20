"""班次数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ShiftType:
    """班次类型定义。"""

    shift_type_id: str
    name: str
    start_time: str          # HH:MM
    end_time: str            # HH:MM（可跨天，如夜班 22:00~06:00）
    grace_minutes: int = 5   # 迟到/早退宽限
    break_minutes: int = 60  # 扣除的休息时长

    def to_dict(self) -> dict:
        return {
            "shift_type_id": self.shift_type_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "grace_minutes": self.grace_minutes,
            "break_minutes": self.break_minutes,
        }


@dataclass
class ShiftAssignment:
    """员工某天的班次安排。"""

    employee_id: str
    date: str
    shift_type_id: str
    required: bool = True    # 是否必须出勤（请假/调休则 False）

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "date": self.date,
            "shift_type_id": self.shift_type_id,
            "required": self.required,
        }


@dataclass
class ShiftResult:
    """按班次判定后的出勤结果。"""

    employee_id: str
    date: str
    shift_type_id: str
    shift_name: str
    first_in: Optional[str] = None
    last_out: Optional[str] = None
    actual_hours: float = 0.0
    expected_hours: float = 0.0
    anomalies: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "date": self.date,
            "shift_type_id": self.shift_type_id,
            "shift_name": self.shift_name,
            "first_in": self.first_in,
            "last_out": self.last_out,
            "actual_hours": round(self.actual_hours, 2),
            "expected_hours": round(self.expected_hours, 2),
            "anomalies": self.anomalies,
        }
