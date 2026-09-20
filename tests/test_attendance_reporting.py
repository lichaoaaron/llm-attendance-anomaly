"""报告、导入、部门聚合服务单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.services.department_aggregation import DepartmentAggregationService
from attendance_anomaly.services.importer import PunchImporter
from attendance_anomaly.services.performance_assist import PerformanceAssistService
from attendance_anomaly.services.report_service import ReportService


def _day(emp_id, date="2026-09-14", first_in="09:00", last_out="18:00", work_hours=9.0) -> AttendanceDay:
    return AttendanceDay(employee_id=emp_id, date=date, first_in=first_in, last_out=last_out, work_hours=work_hours)


class TestImporter(unittest.TestCase):
    def test_import_valid(self) -> None:
        csv_text = "员工编号,日期,打卡时间,打卡类型\nA1,2026-09-14,09:00,in\nA1,2026-09-14,18:00,out\n"
        result = PunchImporter().import_csv(csv_text)
        self.assertEqual(len(result.records), 2)

    def test_invalid_type(self) -> None:
        csv_text = "员工编号,日期,打卡时间,打卡类型\nA1,2026-09-14,09:00,unknown\n"
        result = PunchImporter().import_csv(csv_text)
        self.assertEqual(len(result.records), 0)
        self.assertTrue(any("打卡类型非法" in e for e in result.errors))


class TestReportService(unittest.TestCase):
    def test_csv(self) -> None:
        csv_text = ReportService().to_csv([{"a": "1", "b": "2"}])
        self.assertIn("a,b", csv_text)

    def test_markdown(self) -> None:
        md = ReportService().to_markdown_table([{"a": "1"}])
        self.assertIn("| a |", md)

    def test_html_escape(self) -> None:
        html_text = ReportService().to_html_page("t", [{"rows": [{"a": "<x>"}]}])
        self.assertIn("&lt;x&gt;", html_text)


class TestDepartmentAggregation(unittest.TestCase):
    def test_aggregate(self) -> None:
        perf = PerformanceAssistService(AppConfig())
        service = DepartmentAggregationService(perf)
        days = [_day("A1", "2026-09-14"), _day("A2", "2026-09-14")]
        departments = {"A1": "研发", "A2": "研发"}
        results = service.aggregate(days, anomalies=[], employee_departments=departments, expected_work_days=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].department, "研发")
        self.assertEqual(results[0].headcount, 2)


if __name__ == "__main__":
    unittest.main()
