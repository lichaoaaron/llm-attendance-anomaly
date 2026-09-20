"""考勤流水清洗服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import PunchRecord
from attendance_anomaly.services.attendance_cleaner import AttendanceCleaner


class TestAttendanceCleaner(unittest.TestCase):
    def setUp(self) -> None:
        self.cleaner = AttendanceCleaner()

    def test_dedup_and_pair(self) -> None:
        records = [
            PunchRecord("A1", "2026-09-14", "09:00", "in"),
            PunchRecord("A1", "2026-09-14", "18:00", "out"),
            PunchRecord("A1", "2026-09-14", "18:00", "out"),  # 重复打卡
        ]
        days = self.cleaner.clean(records)
        self.assertEqual(len(days), 1)
        self.assertEqual(days[0].first_in, "09:00")
        self.assertEqual(days[0].last_out, "18:00")
        self.assertAlmostEqual(days[0].work_hours, 9.0)

    def test_work_hours_calculation(self) -> None:
        records = [
            PunchRecord("A1", "2026-09-14", "09:00", "in"),
            PunchRecord("A1", "2026-09-14", "12:00", "out"),
            PunchRecord("A1", "2026-09-14", "13:00", "in"),
            PunchRecord("A1", "2026-09-14", "18:00", "out"),
        ]
        days = self.cleaner.clean(records)
        # 上午 3 小时 + 下午 5 小时 = 8 小时。
        self.assertAlmostEqual(days[0].work_hours, 8.0)

    def test_missing_out(self) -> None:
        records = [PunchRecord("A1", "2026-09-14", "09:00", "in")]
        days = self.cleaner.clean(records)
        self.assertIsNone(days[0].last_out)
        self.assertEqual(days[0].work_hours, 0.0)

    def test_group_by_employee_and_date(self) -> None:
        records = [
            PunchRecord("A1", "2026-09-14", "09:00", "in"),
            PunchRecord("A1", "2026-09-14", "18:00", "out"),
            PunchRecord("A2", "2026-09-14", "09:00", "in"),
            PunchRecord("A2", "2026-09-14", "18:00", "out"),
        ]
        days = self.cleaner.clean(records)
        self.assertEqual(len(days), 2)


if __name__ == "__main__":
    unittest.main()
