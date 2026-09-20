"""月度合规报告服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.models.leave import LeaveRequest
from attendance_anomaly.services.compliance_report import ComplianceReportService
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.monthly_settlement import MonthlySettlementService
from attendance_anomaly.services.work_hours_policy import WorkHoursPolicy, WorkHoursPolicyService


class TestComplianceReport(unittest.TestCase):
    def test_generate(self) -> None:
        calendar = WorkingCalendar([])
        leave = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-16", "2026-09-16")])
        settlement = MonthlySettlementService(calendar, leave)
        work_hours = WorkHoursPolicyService({"A1": WorkHoursPolicy.STANDARD})
        service = ComplianceReportService(settlement, work_hours)

        days = [
            AttendanceDay(employee_id="A1", date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=8.0),
            AttendanceDay(employee_id="A1", date="2026-09-15", first_in="09:00", last_out="18:00", work_hours=8.0),
        ]
        records = service.generate(["A1"], "2026-09", days, anomalies=[])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].present_days, 2)
        self.assertTrue(records[0].compliant)


if __name__ == "__main__":
    unittest.main()
