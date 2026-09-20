"""考勤分析编排引擎。

把流水清洗、异常识别、请假校验、绩效评估、部门聚合等流程编排为一次完整
分析，输出统一的结构化报告。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.services.absenteeism_service import AbsenteeismService
from attendance_anomaly.services.anomaly_engine import AnomalyEngine
from attendance_anomaly.services.attendance_cleaner import AttendanceCleaner
from attendance_anomaly.services.department_aggregation import DepartmentAggregationService
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.performance_assist import PerformanceAssistService


@dataclass
class AttendanceReport:
    """一次完整考勤分析产出。"""

    days: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    department_attendance: List[Dict[str, Any]] = field(default_factory=list)
    leave_conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "days": self.days,
            "anomalies": self.anomalies,
            "summaries": self.summaries,
            "department_attendance": self.department_attendance,
            "leave_conflicts": self.leave_conflicts,
        }


class AttendanceAnalysisEngine:
    """考勤分析编排引擎。"""

    def __init__(self, config: AppConfig, calendar: WorkingCalendar, leave_service: LeaveService) -> None:
        self._cleaner = AttendanceCleaner()
        self._anomaly = AnomalyEngine(config)
        self._performance = PerformanceAssistService(config)
        self._department = DepartmentAggregationService(self._performance)
        self._absenteeism = AbsenteeismService(calendar, leave_service)
        self._leave = leave_service

    def run(
        self,
        punches,
        employee_departments: Dict[str, str],
        start_date: str,
        end_date: str,
        expected_work_days: int,
    ) -> AttendanceReport:
        """执行完整考勤分析流程。"""
        days: List[AttendanceDay] = self._cleaner.clean(punches)
        anomalies: List[Anomaly] = self._anomaly.detect(days)
        anomalies.extend(self._absenteeism.detect_absent(days, start_date, end_date))
        anomalies.extend(self._absenteeism.detect_weekend_overtime(days))
        anomalies.extend(self._absenteeism.detect_consecutive_work(days))

        summaries = [s.to_dict() for s in self._performance.summarize(days, expected_work_days)]
        department = [
            m.to_dict()
            for m in self._department.aggregate(days, anomalies, employee_departments, expected_work_days)
        ]
        conflicts = [c.to_dict() for c in self._leave.find_conflicts(days)]

        return AttendanceReport(
            days=[d.to_dict() for d in days],
            anomalies=[a.to_dict() for a in anomalies],
            summaries=summaries,
            department_attendance=department,
            leave_conflicts=conflicts,
        )
