"""月度合规报告服务。

汇总员工月度工时合规、异常数量、出勤情况，生成一份可供 HR 存档的
月度考勤合规报告。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.services.monthly_settlement import MonthlySettlementService
from attendance_anomaly.services.work_hours_policy import WorkHoursPolicyService, WorkHoursResult


@dataclass
class ComplianceRecord:
    """单名员工的月度合规记录。"""

    employee_id: str
    year_month: str
    present_days: int
    expected_work_days: int
    anomaly_count: int
    total_hours: float
    monthly_cap: float
    compliant: bool

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "year_month": self.year_month,
            "present_days": self.present_days,
            "expected_work_days": self.expected_work_days,
            "anomaly_count": self.anomaly_count,
            "total_hours": round(self.total_hours, 2),
            "monthly_cap": self.monthly_cap,
            "compliant": self.compliant,
        }


class ComplianceReportService:
    """月度合规报告生成。"""

    def __init__(
        self,
        settlement_service: MonthlySettlementService,
        work_hours_service: WorkHoursPolicyService,
    ) -> None:
        self._settlement = settlement_service
        self._work_hours = work_hours_service

    def generate(
        self,
        employee_ids: List[str],
        year_month: str,
        days: List[AttendanceDay],
        anomalies: List[Anomaly],
    ) -> List[ComplianceRecord]:
        """为一批员工生成月度合规记录。"""
        records: List[ComplianceRecord] = []
        for emp_id in employee_ids:
            settlement = self._settlement.settle(emp_id, year_month, days, anomalies)
            hours_result = self._work_hours.analyze(emp_id, year_month, days)
            my_anomaly_count = sum(
                1 for a in anomalies if a.employee_id == emp_id and a.date.startswith(year_month)
            )
            records.append(
                ComplianceRecord(
                    employee_id=emp_id,
                    year_month=year_month,
                    present_days=settlement.present_days,
                    expected_work_days=settlement.expected_work_days,
                    anomaly_count=my_anomaly_count,
                    total_hours=hours_result.total_hours,
                    monthly_cap=hours_result.monthly_cap,
                    compliant=hours_result.compliant,
                )
            )
        records.sort(key=lambda r: r.employee_id)
        return records
