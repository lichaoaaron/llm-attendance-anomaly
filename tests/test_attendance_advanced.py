"""加班、月度结算、分析引擎单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.models.leave import LeaveRequest
from attendance_anomaly.models.overtime import OvertimeRequest
from attendance_anomaly.sample_data import SampleAttendanceGenerator
from attendance_anomaly.services.analysis_engine import AttendanceAnalysisEngine
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.monthly_settlement import MonthlySettlementService
from attendance_anomaly.services.overtime_service import OvertimeService


class TestOvertimeService(unittest.TestCase):
    def test_summarize(self) -> None:
        service = OvertimeService(
            [
                OvertimeRequest("R1", "A1", "2026-09-14", 3.0),
                OvertimeRequest("R2", "A1", "2026-09-15", 2.0, compensated=True),
            ]
        )
        summary = service.summarize()[0]
        self.assertAlmostEqual(summary.total_hours, 5.0)
        self.assertAlmostEqual(summary.remaining_hours, 3.0)

    def test_hours_on(self) -> None:
        service = OvertimeService([OvertimeRequest("R1", "A1", "2026-09-14", 3.0)])
        self.assertAlmostEqual(service.hours_on("A1", "2026-09-14"), 3.0)
        self.assertAlmostEqual(service.hours_on("A1", "2026-09-15"), 0.0)


class TestMonthlySettlement(unittest.TestCase):
    def test_settle(self) -> None:
        calendar = WorkingCalendar([])
        leave = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-16", "2026-09-16")])
        service = MonthlySettlementService(calendar, leave)
        days = [
            AttendanceDay(employee_id="A1", date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=9.0),
            AttendanceDay(employee_id="A1", date="2026-09-15", first_in="09:00", last_out="18:00", work_hours=9.0),
        ]
        settlement = service.settle("A1", "2026-09", days, anomalies=[])
        self.assertEqual(settlement.present_days, 2)
        self.assertEqual(settlement.leave_days, 1)


class TestAnalysisEngine(unittest.TestCase):
    def test_run(self) -> None:
        calendar = WorkingCalendar([])
        leave = LeaveService([])
        engine = AttendanceAnalysisEngine(AppConfig(), calendar, leave)
        punches = SampleAttendanceGenerator(seed=1).generate(["A1"], "2026-09-14", 3)
        report = engine.run(punches, {"A1": "研发"}, "2026-09-14", "2026-09-16", expected_work_days=3)
        data = report.to_dict()
        self.assertIn("anomalies", data)
        self.assertIn("summaries", data)
        self.assertIn("department_attendance", data)


if __name__ == "__main__":
    unittest.main()
