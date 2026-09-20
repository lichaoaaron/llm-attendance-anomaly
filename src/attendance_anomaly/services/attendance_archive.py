"""考勤归档服务。

把某月的考勤数据归档为汇总快照，包含出勤、异常、加班、请假等维度，
支持导出与留存。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.utils.statistics import frequency_distribution


@dataclass
class MonthlyArchive:
    """月度考勤归档快照。"""

    year_month: str
    employee_count: int
    total_present_days: int
    total_anomalies: int
    anomaly_distribution: Dict[str, int] = field(default_factory=dict)
    avg_work_hours: float = 0.0
    leave_totals: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "year_month": self.year_month,
            "employee_count": self.employee_count,
            "total_present_days": self.total_present_days,
            "total_anomalies": self.total_anomalies,
            "anomaly_distribution": self.anomaly_distribution,
            "avg_work_hours": round(self.avg_work_hours, 2),
            "leave_totals": self.leave_totals,
        }


class AttendanceArchiveService:
    """考勤归档服务。"""

    def __init__(self, leave_service: LeaveService) -> None:
        self._leave = leave_service

    def archive(
        self,
        year_month: str,
        days: List[AttendanceDay],
        anomalies: List[Anomaly],
    ) -> MonthlyArchive:
        """归档某月考勤数据。"""
        month_days = [d for d in days if d.date.startswith(year_month)]
        month_anomalies = [a for a in anomalies if a.date.startswith(year_month)]

        employees = {d.employee_id for d in month_days} | {a.employee_id for a in month_anomalies}
        present = sum(1 for d in month_days if d.first_in is not None and d.last_out is not None)
        work_hours = [d.work_hours for d in month_days]
        avg_hours = sum(work_hours) / len(work_hours) if work_hours else 0.0

        leave_totals: Dict[str, int] = {}
        for emp_id in employees:
            leave_days = sum(1 for d in self._leave.leave_dates_for(emp_id) if d.startswith(year_month))
            if leave_days:
                leave_totals[emp_id] = leave_days

        return MonthlyArchive(
            year_month=year_month,
            employee_count=len(employees),
            total_present_days=present,
            total_anomalies=len(month_anomalies),
            anomaly_distribution=frequency_distribution(a.anomaly_type for a in month_anomalies),
            avg_work_hours=avg_hours,
            leave_totals=leave_totals,
        )
