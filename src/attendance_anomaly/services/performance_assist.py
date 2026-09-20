"""绩效辅助评估服务。

基于考勤汇总数据计算出勤率、平均迟到时长、加班时长等指标，
给出辅助性的绩效参考结论（供 HR 参考，不替代正式绩效评估）。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.services.anomaly_engine import _to_minutes


@dataclass
class AttendanceSummary:
    """单个员工的考勤绩效摘要。"""

    employee_id: str
    work_days: int
    attendance_rate: float
    avg_lateness_minutes: float
    total_overtime_hours: float
    conclusion: str

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "work_days": self.work_days,
            "attendance_rate": round(self.attendance_rate, 4),
            "avg_lateness_minutes": round(self.avg_lateness_minutes, 2),
            "total_overtime_hours": round(self.total_overtime_hours, 2),
            "conclusion": self.conclusion,
        }


class PerformanceAssistService:
    """考勤绩效辅助评估。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def summarize(self, days: List[AttendanceDay], expected_work_days: int) -> List[AttendanceSummary]:
        grouped: Dict[str, List[AttendanceDay]] = {}
        for day in days:
            grouped.setdefault(day.employee_id, []).append(day)

        summaries: List[AttendanceSummary] = []
        for employee_id, emp_days in sorted(grouped.items()):
            present = sum(1 for d in emp_days if d.first_in is not None and d.last_out is not None)
            attendance_rate = present / expected_work_days if expected_work_days else 0.0

            lateness: List[int] = []
            for d in emp_days:
                if d.first_in is not None:
                    delta = _to_minutes(d.first_in) - self.config.start_minutes
                    if delta > 0:
                        lateness.append(delta)
            avg_lateness = sum(lateness) / len(lateness) if lateness else 0.0

            total_overtime = sum(max(0.0, d.work_hours - 9.0) for d in emp_days)

            conclusion = self._conclusion(attendance_rate, avg_lateness)
            summaries.append(
                AttendanceSummary(
                    employee_id=employee_id,
                    work_days=len(emp_days),
                    attendance_rate=attendance_rate,
                    avg_lateness_minutes=avg_lateness,
                    total_overtime_hours=round(total_overtime, 2),
                    conclusion=conclusion,
                )
            )
        return summaries

    @staticmethod
    def _conclusion(attendance_rate: float, avg_lateness: float) -> str:
        """根据出勤率与迟到情况给出辅助结论。"""
        if attendance_rate >= 0.95 and avg_lateness <= 5:
            return "考勤表现优秀"
        if attendance_rate >= 0.85 and avg_lateness <= 15:
            return "考勤表现良好"
        if attendance_rate < 0.8:
            return "出勤率偏低，建议关注"
        return "存在迟到情况，建议提醒"
