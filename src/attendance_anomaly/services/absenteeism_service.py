"""缺勤与连班识别服务。

在基础异常（迟到/早退/缺卡/加班）之外，识别旷工、连续上班、休息日加班等
需要结合工作日历与请假信息的异常类型。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.utils.time_utils import add_days


@dataclass
class AbsenteeismResult:
    """缺勤/连班识别结果集合。"""

    anomalies: List[Anomaly] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.anomalies is None:
            self.anomalies = []


class AbsenteeismService:
    """旷工、连班、休息日加班识别服务。"""

    def __init__(self, calendar: WorkingCalendar, leave_service: LeaveService) -> None:
        self._calendar = calendar
        self._leave = leave_service

    def detect_absent(self, days: List[AttendanceDay], start_date: str, end_date: str) -> List[Anomaly]:
        """识别旷工：工作日既无打卡又无请假记录。"""
        present: Set[str] = {f"{d.employee_id}|{d.date}" for d in days}
        employees = {d.employee_id for d in days}
        anomalies: List[Anomaly] = []

        current = start_date
        while current <= end_date:
            if not self._calendar.is_workday(current):
                current = add_days(current, 1)
                continue
            for emp_id in employees:
                if f"{emp_id}|{current}" in present:
                    continue
                if self._leave.is_on_leave(emp_id, current):
                    continue
                anomalies.append(
                    Anomaly(
                        employee_id=emp_id,
                        date=current,
                        anomaly_type="absent",
                        severity="high",
                        detail="工作日无打卡且无请假记录，疑似旷工",
                    )
                )
            current = add_days(current, 1)
        return anomalies

    def detect_weekend_overtime(self, days: List[AttendanceDay]) -> List[Anomaly]:
        """识别休息日加班：休息日存在打卡记录。"""
        anomalies: List[Anomaly] = []
        for day in days:
            if day.first_in is None and day.last_out is None:
                continue
            if not self._calendar.is_workday(day.date):
                anomalies.append(
                    Anomaly(
                        employee_id=day.employee_id,
                        date=day.date,
                        anomaly_type="weekend_overtime",
                        severity="low",
                        detail="休息日存在打卡记录",
                    )
                )
        return anomalies

    def detect_consecutive_work(self, days: List[AttendanceDay], max_consecutive: int = 6) -> List[Anomaly]:
        """识别连班：连续上班天数超过阈值。"""
        worked_dates: Dict[str, Set[str]] = {}
        for day in days:
            if day.first_in is None and day.last_out is None:
                continue
            worked_dates.setdefault(day.employee_id, set()).add(day.date)

        anomalies: List[Anomaly] = []
        for emp_id, dates in worked_dates.items():
            sorted_dates = sorted(dates)
            streak = 1
            longest = 1
            last_date = sorted_dates[0] if sorted_dates else ""
            for date in sorted_dates[1:]:
                if add_days(last_date, 1) == date:
                    streak += 1
                    longest = max(longest, streak)
                else:
                    streak = 1
                last_date = date
            if longest > max_consecutive:
                anomalies.append(
                    Anomaly(
                        employee_id=emp_id,
                        date=last_date,
                        anomaly_type="consecutive_work",
                        severity="medium",
                        detail=f"连续上班 {longest} 天，超过阈值 {max_consecutive} 天",
                    )
                )
        return anomalies
