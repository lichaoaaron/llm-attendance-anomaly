"""加班管理服务。

管理加班申请，汇总加班时长与调休抵扣，输出可调休余额。
"""
from __future__ import annotations

from typing import Dict, List

from attendance_anomaly.models.overtime import OvertimeRequest, OvertimeSummary


class OvertimeService:
    """加班申请与调休管理。"""

    def __init__(self, requests: List[OvertimeRequest]) -> None:
        self._requests = [r for r in requests if r.status == "approved"]

    def summarize(self) -> List[OvertimeSummary]:
        """按员工汇总加班时长与调休余额。"""
        grouped: Dict[str, List[OvertimeRequest]] = {}
        for request in self._requests:
            grouped.setdefault(request.employee_id, []).append(request)

        summaries: List[OvertimeSummary] = []
        for employee_id, requests in sorted(grouped.items()):
            total = sum(r.hours for r in requests)
            compensated = sum(r.hours for r in requests if r.compensated)
            summaries.append(
                OvertimeSummary(
                    employee_id=employee_id,
                    total_hours=total,
                    request_count=len(requests),
                    compensated_hours=compensated,
                    remaining_hours=max(0.0, total - compensated),
                )
            )
        summaries.sort(key=lambda s: s.total_hours, reverse=True)
        return summaries

    def hours_on(self, employee_id: str, date: str) -> float:
        """返回员工某天的已批准加班时长。"""
        return sum(r.hours for r in self._requests if r.employee_id == employee_id and r.date == date)

    def monthly_hours(self, employee_id: str, year_month: str) -> float:
        """返回员工某月（YYYY-MM）的加班总时长。"""
        return sum(
            r.hours for r in self._requests
            if r.employee_id == employee_id and r.date.startswith(year_month)
        )
