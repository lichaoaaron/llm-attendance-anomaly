"""考勤异常识别引擎单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.services.anomaly_engine import AnomalyEngine


def _day(first_in=None, last_out=None, work_hours=8.0) -> AttendanceDay:
    return AttendanceDay(
        employee_id="A1",
        date="2026-09-14",
        first_in=first_in,
        last_out=last_out,
        work_hours=work_hours,
    )


class TestAnomalyEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = AnomalyEngine(AppConfig())

    def test_late(self) -> None:
        anomalies = self.engine.detect([_day(first_in="09:30", last_out="18:00")])
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("late", types)

    def test_early_leave(self) -> None:
        anomalies = self.engine.detect([_day(first_in="09:00", last_out="17:00")])
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("early_leave", types)

    def test_missing_punch(self) -> None:
        anomalies = self.engine.detect([_day(first_in="09:00", last_out=None)])
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("missing_punch", types)

    def test_overtime(self) -> None:
        anomalies = self.engine.detect([_day(first_in="09:00", last_out="20:00", work_hours=11.0)])
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("overtime", types)

    def test_no_anomaly(self) -> None:
        anomalies = self.engine.detect([_day(first_in="09:00", last_out="18:00", work_hours=9.0)])
        self.assertEqual(anomalies, [])


if __name__ == "__main__":
    unittest.main()
