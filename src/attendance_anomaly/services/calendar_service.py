"""工作日历服务。

结合节假日与调休配置，提供应出勤天数统计、工作日区间遍历等能力，
供绩效评估与月度报表使用。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from attendance_anomaly.models.holiday import Holiday, WorkingCalendar
from attendance_anomaly.utils.time_utils import add_days


@dataclass
class MonthCalendar:
    """某月的工作日统计。"""

    year: int
    month: int
    total_days: int
    work_days: int
    rest_days: int

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "total_days": self.total_days,
            "work_days": self.work_days,
            "rest_days": self.rest_days,
        }


class CalendarService:
    """工作日历服务。"""

    def __init__(self, calendar: WorkingCalendar) -> None:
        self._calendar = calendar

    def work_days_between(self, start_date: str, end_date: str) -> int:
        """统计闭区间 [start_date, end_date] 内的工作日数量。"""
        count = 0
        current = start_date
        while current <= end_date:
            if self._calendar.is_workday(current):
                count += 1
            current = add_days(current, 1)
        return count

    def month_summary(self, year: int, month: int) -> MonthCalendar:
        """统计某个月的工作日情况。"""
        first = datetime(year, month, 1)
        if month == 12:
            last = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last = datetime(year, month + 1, 1) - timedelta(days=1)
        total_days = last.day
        work_days = self.work_days_between(first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d"))
        return MonthCalendar(
            year=year,
            month=month,
            total_days=total_days,
            work_days=work_days,
            rest_days=total_days - work_days,
        )

    def list_workdays(self, start_date: str, end_date: str) -> List[str]:
        """列出区间内的所有工作日日期。"""
        result: List[str] = []
        current = start_date
        while current <= end_date:
            if self._calendar.is_workday(current):
                result.append(current)
            current = add_days(current, 1)
        return result
