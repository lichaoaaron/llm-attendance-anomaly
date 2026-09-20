"""考勤趋势分析单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.services.trend_analysis import TrendAnalysisService


def _day(date, work_hours=8.0) -> AttendanceDay:
    return AttendanceDay(employee_id="A1", date=date, first_in="09:00", last_out="18:00", work_hours=work_hours)


class TestTrendAnalysisService(unittest.TestCase):
    def test_trend_points(self) -> None:
        days = [_day("2026-09-14"), _day("2026-09-15"), _day("2026-09-21")]
        anomalies = [Anomaly("A1", "2026-09-14", "late", "medium", "迟到")]
        report = TrendAnalysisService().analyze(["2026-09-14", "2026-09-21"], days, anomalies)
        self.assertEqual(len(report.points), 2)
        self.assertEqual(report.points[0].late_count, 1)

    def test_trend_direction(self) -> None:
        days = [_day("2026-09-14", 8.0), _day("2026-09-21", 10.0)]
        report = TrendAnalysisService().analyze(["2026-09-14", "2026-09-21"], days, [])
        self.assertEqual(report.overtime_trend, "rising")


if __name__ == "__main__":
    unittest.main()
