"""月度考勤结算服务。

按员工汇总一个月内的出勤、缺勤、迟到、早退、加班等指标，
生成月度考勤结算结果，供薪资核算与绩效评估参考。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.utils.statistics import frequency_distribution


@dataclass
class MonthlySettlement:
    """员工月度考勤结算。"""

    employee_id: str
    year_month: str
    present_days: int
    expected_work_days: int
    late_count: int
    early_leave_count: int
    absent_count: int
    overtime_total_hours: float
    leave_days: int
    anomaly_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "year_month": self.year_month,
            "present_days": self.present_days,
            "expected_work_days": self.expected_work_days,
            "late_count": self.late_count,
            "early_leave_count": self.early_leave_count,
            "absent_count": self.absent_count,
            "overtime_total_hours": round(self.overtime_total_hours, 2),
            "leave_days": self.leave_days,
            "anomaly_distribution": self.anomaly_distribution,
        }


class MonthlySettlementService:
    """月度考勤结算。"""

    def __init__(self, calendar: WorkingCalendar, leave_service: LeaveService) -> None:
        self._calendar = calendar
        self._leave = leave_service

    def settle(
        self,
        employee_id: str,
        year_month: str,
        days: List[AttendanceDay],
        anomalies: List[Anomaly],
    ) -> MonthlySettlement:
        """结算某员工某月的考勤。"""
        my_days = [d for d in days if d.employee_id == employee_id and d.date.startswith(year_month)]
        my_anomalies = [a for a in anomalies if a.employee_id == employee_id and a.date.startswith(year_month)]

        present = sum(1 for d in my_days if d.first_in is not None and d.last_out is not None)
        late = sum(1 for a in my_anomalies if a.anomaly_type == "late")
        early = sum(1 for a in my_anomalies if a.anomaly_type == "early_leave")
        absent = sum(1 for a in my_anomalies if a.anomaly_type == "absent")
        overtime_hours = sum(max(0.0, d.work_hours - 9.0) for d in my_days)

        # 该月应出勤天数 = 该月工作日数。
        expected = self._expected_work_days(year_month)
        leave_days = self._leave_days_in_month(employee_id, year_month)

        distribution = frequency_distribution(a.anomaly_type for a in my_anomalies)

        return MonthlySettlement(
            employee_id=employee_id,
            year_month=year_month,
            present_days=present,
            expected_work_days=expected,
            late_count=late,
            early_leave_count=early,
            absent_count=absent,
            overtime_total_hours=round(overtime_hours, 2),
            leave_days=leave_days,
            anomaly_distribution=distribution,
        )

    def _expected_work_days(self, year_month: str) -> int:
        year, month = int(year_month[:4]), int(year_month[5:7])
        from attendance_anomaly.services.calendar_service import CalendarService
        return CalendarService(self._calendar).month_summary(year, month).work_days

    def _leave_days_in_month(self, employee_id: str, year_month: str) -> int:
        leave_dates = self._leave.leave_dates_for(employee_id)
        return sum(1 for d in leave_dates if d.startswith(year_month))
