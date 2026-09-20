"""班次、日历、请假、缺勤服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.holiday import Holiday, WorkingCalendar
from attendance_anomaly.models.leave import LeaveRequest
from attendance_anomaly.models.shift import ShiftAssignment, ShiftType
from attendance_anomaly.services.absenteeism_service import AbsenteeismService
from attendance_anomaly.services.calendar_service import CalendarService
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.shift_service import ShiftService


def _day(emp_id="A1", date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=9.0) -> AttendanceDay:
    return AttendanceDay(employee_id=emp_id, date=date, first_in=first_in, last_out=last_out, work_hours=work_hours)


class TestShiftService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ShiftService([ShiftType("STD", "标准班", "09:00", "18:00", grace_minutes=5, break_minutes=60)])

    def test_normal_no_anomaly(self) -> None:
        assignment = ShiftAssignment("A1", "2026-09-14", "STD")
        result = self.service.evaluate(assignment, _day())
        self.assertEqual(result.anomalies, [])

    def test_late(self) -> None:
        assignment = ShiftAssignment("A1", "2026-09-14", "STD")
        result = self.service.evaluate(assignment, _day(first_in="09:30"))
        self.assertIn("迟到", result.anomalies)

    def test_not_required_skips(self) -> None:
        assignment = ShiftAssignment("A1", "2026-09-14", "STD", required=False)
        result = self.service.evaluate(assignment, None)
        self.assertEqual(result.anomalies, [])


class TestCalendarService(unittest.TestCase):
    def test_workday(self) -> None:
        calendar = WorkingCalendar([Holiday("2026-10-01", "国庆节", is_rest=True)])
        service = CalendarService(calendar)
        self.assertTrue(service._calendar.is_workday("2026-09-14"))
        self.assertFalse(service._calendar.is_workday("2026-10-01"))

    def test_adjust_workday(self) -> None:
        # 调休：周六上班（is_rest=False）。
        calendar = WorkingCalendar([Holiday("2026-09-19", "调休", is_rest=False)])
        service = CalendarService(calendar)
        self.assertTrue(service._calendar.is_workday("2026-09-19"))

    def test_month_summary(self) -> None:
        service = CalendarService(WorkingCalendar([]))
        summary = service.month_summary(2026, 9)
        self.assertEqual(summary.total_days, 30)
        self.assertGreater(summary.work_days, 0)


class TestLeaveService(unittest.TestCase):
    def test_expand_dates(self) -> None:
        request = LeaveRequest("R1", "A1", "annual", "2026-09-14", "2026-09-16")
        dates = LeaveService([]).expand_dates(request)
        self.assertEqual(dates, ["2026-09-14", "2026-09-15", "2026-09-16"])

    def test_is_on_leave(self) -> None:
        service = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-14", "2026-09-15")])
        self.assertTrue(service.is_on_leave("A1", "2026-09-14"))
        self.assertFalse(service.is_on_leave("A1", "2026-09-16"))

    def test_find_conflicts(self) -> None:
        service = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-14", "2026-09-15")])
        conflicts = service.find_conflicts([_day(date="2026-09-14")])
        self.assertEqual(len(conflicts), 1)

    def test_summarize(self) -> None:
        service = LeaveService([LeaveRequest("R1", "A1", "annual", "2026-09-14", "2026-09-15")])
        summaries = service.summarize()
        self.assertEqual(summaries[0].total_days, 2)


class TestAbsenteeismService(unittest.TestCase):
    def test_detect_absent(self) -> None:
        calendar = WorkingCalendar([])
        leave = LeaveService([])
        service = AbsenteeismService(calendar, leave)
        days = [_day(date="2026-09-14")]  # 只有 A1 周一有记录
        anomalies = service.detect_absent(days, "2026-09-14", "2026-09-15")
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("absent", types)  # 周二 A1 无记录且无请假 -> 旷工

    def test_detect_weekend_overtime(self) -> None:
        calendar = WorkingCalendar([])
        service = AbsenteeismService(calendar, LeaveService([]))
        anomalies = service.detect_weekend_overtime([_day(date="2026-09-19")])  # 周六
        types = [a.anomaly_type for a in anomalies]
        self.assertIn("weekend_overtime", types)

    def test_detect_consecutive(self) -> None:
        service = AbsenteeismService(WorkingCalendar([]), LeaveService([]))
        days = [_day(date=f"2026-09-{14 + i}") for i in range(7)]
        anomalies = service.detect_consecutive_work(days, max_consecutive=6)
        self.assertEqual(len(anomalies), 1)


if __name__ == "__main__":
    unittest.main()
