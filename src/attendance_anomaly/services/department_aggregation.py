"""部门考勤聚合服务。

把员工级别的考勤指标聚合到部门级别，输出部门出勤率、异常分布、加班均值等
指标，供管理层横向对比。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.services.performance_assist import PerformanceAssistService
from attendance_anomaly.utils.statistics import frequency_distribution, mean


@dataclass
class DepartmentAttendance:
    """部门考勤聚合结果。"""

    department: str
    headcount: int
    avg_attendance_rate: float
    avg_lateness_minutes: float
    total_anomalies: int
    anomaly_distribution: Dict[str, int] = field(default_factory=dict)
    overtime_total_hours: float = 0.0

    def to_dict(self) -> dict:
        return {
            "department": self.department,
            "headcount": self.headcount,
            "avg_attendance_rate": round(self.avg_attendance_rate, 4),
            "avg_lateness_minutes": round(self.avg_lateness_minutes, 2),
            "total_anomalies": self.total_anomalies,
            "anomaly_distribution": self.anomaly_distribution,
            "overtime_total_hours": round(self.overtime_total_hours, 2),
        }


class DepartmentAggregationService:
    """部门考勤聚合。"""

    def __init__(self, performance_service: PerformanceAssistService) -> None:
        self._performance = performance_service

    def aggregate(
        self,
        days: List[AttendanceDay],
        anomalies: List[Anomaly],
        employee_departments: Dict[str, str],
        expected_work_days: int,
    ) -> List[DepartmentAttendance]:
        """按部门聚合考勤数据。"""
        # 员工 -> 部门。
        day_by_emp: Dict[str, List[AttendanceDay]] = {}
        for day in days:
            day_by_emp.setdefault(day.employee_id, []).append(day)

        summaries = self._performance.summarize(days, expected_work_days)
        summary_by_emp = {s.employee_id: s for s in summaries}

        dept_rates: Dict[str, List[float]] = {}
        dept_late: Dict[str, List[float]] = {}
        dept_overtime: Dict[str, float] = {}
        dept_headcount: Dict[str, set] = {}
        dept_anomalies: Dict[str, List[Anomaly]] = {}

        for emp_id, dept in employee_departments.items():
            dept_headcount.setdefault(dept, set()).add(emp_id)
            summary = summary_by_emp.get(emp_id)
            if summary is not None:
                dept_rates.setdefault(dept, []).append(summary.attendance_rate)
                dept_late.setdefault(dept, []).append(summary.avg_lateness_minutes)
                dept_overtime[dept] = dept_overtime.get(dept, 0.0) + summary.total_overtime_hours

        for anomaly in anomalies:
            dept = employee_departments.get(anomaly.employee_id, "未归属")
            dept_anomalies.setdefault(dept, []).append(anomaly)
            dept_headcount.setdefault(dept, set()).add(anomaly.employee_id)

        results: List[DepartmentAttendance] = []
        for dept, members in sorted(dept_headcount.items()):
            anomalies_of_dept = dept_anomalies.get(dept, [])
            results.append(
                DepartmentAttendance(
                    department=dept,
                    headcount=len(members),
                    avg_attendance_rate=mean(dept_rates.get(dept, [])),
                    avg_lateness_minutes=mean(dept_late.get(dept, [])),
                    total_anomalies=len(anomalies_of_dept),
                    anomaly_distribution=frequency_distribution(a.anomaly_type for a in anomalies_of_dept),
                    overtime_total_hours=dept_overtime.get(dept, 0.0),
                )
            )
        return results
