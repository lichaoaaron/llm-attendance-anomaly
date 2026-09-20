"""工时制度策略服务。

支持标准工时与综合计算工时两种制度，按月累计工时并判断是否超出法定上限，
输出工时合规结论。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from attendance_anomaly.models.attendance import AttendanceDay


class WorkHoursPolicy(str, Enum):
    """工时制度。"""

    STANDARD = "standard"        # 标准工时：8 小时/天
    COMPREHENSIVE = "comprehensive"  # 综合计算工时：按月累计


@dataclass
class WorkHoursResult:
    """工时合规结果。"""

    employee_id: str
    year_month: str
    total_hours: float
    policy: str
    monthly_cap: float
    overtime_beyond_cap: float
    compliant: bool

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "year_month": self.year_month,
            "total_hours": round(self.total_hours, 2),
            "policy": self.policy,
            "monthly_cap": self.monthly_cap,
            "overtime_beyond_cap": round(self.overtime_beyond_cap, 2),
            "compliant": self.compliant,
        }


class WorkHoursPolicyService:
    """工时制度合规分析。"""

    # 各制度下的月工时上限（小时）。
    MONTHLY_CAPS = {
        WorkHoursPolicy.STANDARD: 174.0,          # 21.75 天 × 8 小时
        WorkHoursPolicy.COMPREHENSIVE: 200.0,     # 综合工时月上限
    }

    def __init__(self, policies: Dict[str, WorkHoursPolicy]) -> None:
        self._policies = policies

    def analyze(self, employee_id: str, year_month: str, days: List[AttendanceDay]) -> WorkHoursResult:
        """分析某员工某月的工时合规情况。"""
        my_days = [d for d in days if d.employee_id == employee_id and d.date.startswith(year_month)]
        total_hours = sum(d.work_hours for d in my_days)

        policy = self._policies.get(employee_id, WorkHoursPolicy.STANDARD)
        cap = self.MONTHLY_CAPS[policy]
        beyond = max(0.0, total_hours - cap)

        return WorkHoursResult(
            employee_id=employee_id,
            year_month=year_month,
            total_hours=total_hours,
            policy=policy.value,
            monthly_cap=cap,
            overtime_beyond_cap=round(beyond, 2),
            compliant=beyond == 0.0,
        )
