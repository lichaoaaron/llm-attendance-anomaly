"""请假处理服务。

管理请假申请，处理请假日期范围展开、与考勤记录的冲突检测、
以及请假对出勤判定影响的消除。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.leave import LEAVE_TYPE_LABELS, LeaveConflict, LeaveRequest
from attendance_anomaly.utils.time_utils import add_days


@dataclass
class LeaveSummary:
    """员工请假汇总。"""

    employee_id: str
    total_days: int
    by_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "total_days": self.total_days,
            "by_type": self.by_type,
        }


class LeaveService:
    """请假管理服务。"""

    def __init__(self, requests: List[LeaveRequest]) -> None:
        self._requests = [r for r in requests if r.status == "approved"]

    def expand_dates(self, request: LeaveRequest) -> List[str]:
        """把请假区间展开为日期列表（含首尾）。"""
        if request.end_date < request.start_date:
            return []
        dates: List[str] = []
        current = request.start_date
        while current <= request.end_date:
            dates.append(current)
            current = add_days(current, 1)
        return dates

    def leave_dates_for(self, employee_id: str) -> List[str]:
        """返回某员工所有已批准请假的日期并集。"""
        dates = set()
        for request in self._requests:
            if request.employee_id != employee_id:
                continue
            dates.update(self.expand_dates(request))
        return sorted(dates)

    def is_on_leave(self, employee_id: str, date: str) -> bool:
        """判断员工某天是否在请假中。"""
        return date in set(self.leave_dates_for(employee_id))

    def find_conflicts(self, days: List[AttendanceDay]) -> List[LeaveConflict]:
        """检测请假期间仍有打卡记录的冲突（可能存在漏销假）。"""
        leave_dates: Dict[str, set] = {}
        for request in self._requests:
            leave_dates.setdefault(request.employee_id, set()).update(self.expand_dates(request))

        conflicts: List[LeaveConflict] = []
        for day in days:
            if day.first_in is None and day.last_out is None:
                continue
            dates = leave_dates.get(day.employee_id)
            if dates and day.date in dates:
                conflicts.append(
                    LeaveConflict(
                        employee_id=day.employee_id,
                        date=day.date,
                        leave_type="unknown",
                        detail="请假期间存在打卡记录，请核对是否漏销假",
                    )
                )
        return conflicts

    def summarize(self) -> List[LeaveSummary]:
        """按员工汇总请假天数（按类型统计）。"""
        grouped: Dict[str, Dict[str, int]] = {}
        for request in self._requests:
            days = len(self.expand_dates(request))
            employee_types = grouped.setdefault(request.employee_id, {})
            employee_types[request.leave_type] = employee_types.get(request.leave_type, 0) + days

        summaries: List[LeaveSummary] = []
        for employee_id, by_type in sorted(grouped.items()):
            summaries.append(
                LeaveSummary(
                    employee_id=employee_id,
                    total_days=sum(by_type.values()),
                    by_type={LEAVE_TYPE_LABELS.get(k, k): v for k, v in by_type.items()},
                )
            )
        return summaries
