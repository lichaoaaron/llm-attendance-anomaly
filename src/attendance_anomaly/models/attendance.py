"""考勤数据模型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PunchRecord:
    """一条原始打卡流水。"""

    employee_id: str
    date: str          # YYYY-MM-DD
    punch_time: str    # HH:MM
    punch_type: str    # in / out


@dataclass
class AttendanceDay:
    """某员工某天的出勤汇总。"""

    employee_id: str
    date: str
    first_in: Optional[str] = None
    last_out: Optional[str] = None
    work_hours: float = 0.0

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "date": self.date,
            "first_in": self.first_in,
            "last_out": self.last_out,
            "work_hours": round(self.work_hours, 2),
        }


@dataclass
class Anomaly:
    """一条考勤异常记录。"""

    employee_id: str
    date: str
    anomaly_type: str     # late / early_leave / missing_punch / overtime
    severity: str         # low / medium / high
    detail: str

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "date": self.date,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "detail": self.detail,
        }
