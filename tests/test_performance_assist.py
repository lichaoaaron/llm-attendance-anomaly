"""绩效辅助评估服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.services.performance_assist import PerformanceAssistService


def _day(emp_id: str, first_in: str, last_out: str, work_hours: float) -> AttendanceDay:
    return AttendanceDay(
        employee_id=emp_id,
        date="2026-09-14",
        first_in=first_in,
        last_out=last_out,
        work_hours=work_hours,
    )


class TestPerformanceAssistService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PerformanceAssistService(AppConfig())

    def test_excellent(self) -> None:
        days = [_day("A1", "09:00", "18:00", 9.0)] * 5
        summary = self.service.summarize(days, expected_work_days=5)[0]
        self.assertEqual(summary.conclusion, "考勤表现优秀")

    def test_attendance_rate(self) -> None:
        # 仅 3 天有完整打卡，应出勤 5 天 => 出勤率 0.6。
        present = [_day("A1", "09:00", "18:00", 9.0)] * 3
        missing = [
            AttendanceDay(employee_id="A1", date="2026-09-15", first_in=None, last_out=None),
            AttendanceDay(employee_id="A1", date="2026-09-16", first_in=None, last_out=None),
        ]
        summary = self.service.summarize(present + missing, expected_work_days=5)[0]
        self.assertAlmostEqual(summary.attendance_rate, 0.6)
        self.assertEqual(summary.conclusion, "出勤率偏低，建议关注")

    def test_avg_lateness(self) -> None:
        days = [
            _day("A1", "09:10", "18:00", 9.0),
            _day("A1", "09:20", "18:00", 9.0),
        ]
        summary = self.service.summarize(days, expected_work_days=2)[0]
        self.assertAlmostEqual(summary.avg_lateness_minutes, 15.0)


if __name__ == "__main__":
    unittest.main()
