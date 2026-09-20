"""考勤指标分析服务。

在基础汇总之外，提供出勤稳定性、迟到趋势、加班趋势等衍生指标。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.utils.statistics import mean, stddev
from attendance_anomaly.utils.time_utils import to_minutes


@dataclass
class AttendanceMetrics:
    """员工考勤衍生指标。"""

    employee_id: str
    total_days: int
    present_days: int
    attendance_stability: float      # 出勤稳定性 0~1
    avg_arrival_minutes: float       # 平均到岗时刻（分钟）
    arrival_stddev: float            # 到岗时刻标准差，反映迟到波动
    avg_work_hours: float

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "total_days": self.total_days,
            "present_days": self.present_days,
            "attendance_stability": round(self.attendance_stability, 4),
            "avg_arrival_minutes": round(self.avg_arrival_minutes, 2),
            "arrival_stddev": round(self.arrival_stddev, 2),
            "avg_work_hours": round(self.avg_work_hours, 2),
        }


class AttendanceMetricsService:
    """考勤衍生指标分析。"""

    def analyze(self, employee_id: str, days: List[AttendanceDay]) -> AttendanceMetrics:
        """计算某员工的衍生考勤指标。"""
        my_days = [d for d in days if d.employee_id == employee_id]
        present = [d for d in my_days if d.first_in is not None and d.last_out is not None]

        arrival_times = [to_minutes(d.first_in) for d in present if d.first_in]
        work_hours = [d.work_hours for d in my_days]

        # 出勤稳定性：到岗时刻波动越小越稳定。
        if arrival_times:
            arrival_std = stddev(arrival_times)
            stability = max(0.0, 1.0 - arrival_std / 120.0)
        else:
            arrival_std = 0.0
            stability = 0.0

        return AttendanceMetrics(
            employee_id=employee_id,
            total_days=len(my_days),
            present_days=len(present),
            attendance_stability=stability,
            avg_arrival_minutes=mean(arrival_times),
            arrival_stddev=arrival_std,
            avg_work_hours=mean(work_hours),
        )
