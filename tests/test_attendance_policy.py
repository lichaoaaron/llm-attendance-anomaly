"""工时制度、通知、指标服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.services.attendance_metrics import AttendanceMetricsService
from attendance_anomaly.services.notification_service import NotificationService
from attendance_anomaly.services.work_hours_policy import WorkHoursPolicy, WorkHoursPolicyService


def _day(emp_id, date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=8.0) -> AttendanceDay:
    return AttendanceDay(employee_id=emp_id, date=date, first_in=first_in, last_out=last_out, work_hours=work_hours)


class TestWorkHoursPolicy(unittest.TestCase):
    def test_standard_compliant(self) -> None:
        service = WorkHoursPolicyService({"A1": WorkHoursPolicy.STANDARD})
        days = [_day("A1", work_hours=8.0) for _ in range(20)]
        result = service.analyze("A1", "2026-09", days)
        self.assertTrue(result.compliant)

    def test_comprehensive_beyond_cap(self) -> None:
        service = WorkHoursPolicyService({"A1": WorkHoursPolicy.COMPREHENSIVE})
        days = [_day("A1", work_hours=12.0) for _ in range(20)]  # 240 小时 > 200 上限
        result = service.analyze("A1", "2026-09", days)
        self.assertFalse(result.compliant)
        self.assertGreater(result.overtime_beyond_cap, 0)


class TestNotificationService(unittest.TestCase):
    def test_employee_notification(self) -> None:
        anomalies = [Anomaly("A1", "2026-09-14", "late", "medium", "迟到 25 分钟")]
        notifications = NotificationService().build_notifications(anomalies)
        self.assertEqual(len(notifications), 1)
        self.assertIn("迟到", notifications[0].title)

    def test_manager_digest(self) -> None:
        anomalies = [
            Anomaly("A1", "2026-09-14", "late", "medium", "x"),
            Anomaly("A1", "2026-09-15", "absent", "high", "y"),
        ]
        digests = NotificationService().build_manager_digest(anomalies)
        self.assertEqual(len(digests), 1)
        self.assertIn("2 条异常", digests[0].body)


class TestAttendanceMetrics(unittest.TestCase):
    def test_stability_high(self) -> None:
        days = [_day("A1", first_in="09:00"), _day("A1", first_in="09:05", date="2026-09-15")]
        metrics = AttendanceMetricsService().analyze("A1", days)
        self.assertGreater(metrics.attendance_stability, 0.9)

    def test_present_count(self) -> None:
        days = [_day("A1"), AttendanceDay(employee_id="A1", date="2026-09-15", first_in=None, last_out=None)]
        metrics = AttendanceMetricsService().analyze("A1", days)
        self.assertEqual(metrics.total_days, 2)
        self.assertEqual(metrics.present_days, 1)


if __name__ == "__main__":
    unittest.main()
