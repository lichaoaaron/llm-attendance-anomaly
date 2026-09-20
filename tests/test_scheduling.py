"""排班与归档服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.leave import LeaveRequest
from attendance_anomaly.models.shift import ShiftType
from attendance_anomaly.services.attendance_archive import AttendanceArchiveService
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.scheduling_service import SchedulingService


class TestSchedulingService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SchedulingService([ShiftType("STD", "标准班", "09:00", "18:00")])

    def test_generate_fixed(self) -> None:
        plan = self.service.generate_fixed(["A1", "A2"], "2026-09-14", days=3, shift_type_id="STD")
        # 3 个工作日 × 2 员工。
        self.assertEqual(len(plan.assignments), 6)

    def test_generate_fixed_rest_weekend(self) -> None:
        plan = self.service.generate_fixed(["A1"], "2026-09-19", days=2, shift_type_id="STD", rest_weekends=True)
        # 9-19 周六、9-20 周日，均应休息。
        self.assertEqual(len(plan.assignments), 0)

    def test_generate_rotation(self) -> None:
        plan = self.service.generate_rotation(["A1"], "2026-09-14", days=3, shift_type_ids=["STD"])
        self.assertEqual(len(plan.assignments), 3)

    def test_unknown_shift(self) -> None:
        with self.assertRaises(ValueError):
            self.service.generate_fixed(["A1"], "2026-09-14", 1, "NOPE")


class TestAttendanceArchive(unittest.TestCase):
    def test_archive(self) -> None:
        leave = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-16", "2026-09-16")])
        service = AttendanceArchiveService(leave)
        days = [
            AttendanceDay(employee_id="A1", date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=9.0),
            AttendanceDay(employee_id="A1", date="2026-09-15", first_in="09:00", last_out="18:00", work_hours=8.0),
        ]
        archive = service.archive("2026-09", days, anomalies=[])
        self.assertEqual(archive.employee_count, 1)
        self.assertEqual(archive.total_present_days, 2)
        self.assertAlmostEqual(archive.avg_work_hours, 8.5)
        self.assertEqual(archive.leave_totals["A1"], 1)


if __name__ == "__main__":
    unittest.main()
