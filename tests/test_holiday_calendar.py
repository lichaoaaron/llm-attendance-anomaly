"""节假日生成服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.services.holiday_calendar import HolidayCalendarService


class TestHolidayCalendarService(unittest.TestCase):
    def test_generate_holidays(self) -> None:
        holidays = HolidayCalendarService().generate(2026)
        dates = {h.date for h in holidays}
        self.assertIn("2026-01-01", dates)   # 元旦
        self.assertIn("2026-10-01", dates)   # 国庆
        self.assertGreater(len(holidays), 10)

    def test_calendar_holiday(self) -> None:
        holidays = HolidayCalendarService().generate(2026)
        calendar = WorkingCalendar(holidays)
        self.assertFalse(calendar.is_workday("2026-10-01"))
        self.assertTrue(calendar.is_workday("2026-09-14"))


if __name__ == "__main__":
    unittest.main()
