"""命令行入口。

提供以下子命令：
- clean：清洗考勤流水并输出每日汇总；
- detect：识别考勤异常；
- summarize：输出考勤绩效辅助摘要；
- metrics：输出出勤稳定性等衍生指标；
- notify：为异常生成通知文案；
- report：导出异常/汇总为 CSV / Markdown / HTML。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from attendance_anomaly.config import load_config
from attendance_anomaly.data_loader import load_punches
from attendance_anomaly.models.attendance import PunchRecord
from attendance_anomaly.models.holiday import WorkingCalendar
from attendance_anomaly.services.anomaly_engine import AnomalyEngine
from attendance_anomaly.services.attendance_cleaner import AttendanceCleaner
from attendance_anomaly.services.attendance_metrics import AttendanceMetricsService
from attendance_anomaly.services.leave_service import LeaveService
from attendance_anomaly.services.llm_client import MockLLMClient, OpenAICompatibleClient
from attendance_anomaly.services.monthly_settlement import MonthlySettlementService
from attendance_anomaly.services.notification_service import NotificationService
from attendance_anomaly.services.performance_assist import PerformanceAssistService
from attendance_anomaly.services.report_service import ReportService


def _build_llm(config):
    if config.llm_provider == "openai_compatible":
        return OpenAICompatibleClient(config.llm_api_base, config.llm_api_key, config.llm_model)
    return MockLLMClient()


def _load_data(data_path: Path) -> List[PunchRecord]:
    if not data_path.exists():
        print(f"数据文件不存在：{data_path}", file=sys.stderr)
        sys.exit(1)
    return load_punches(data_path)


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_clean(args, config) -> None:
    days = AttendanceCleaner().clean(_load_data(args.data))
    _print_json([d.to_dict() for d in days])


def cmd_detect(args, config) -> None:
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    anomalies = AnomalyEngine(config).detect(days)
    llm = _build_llm(config)
    output = []
    for a in anomalies:
        item = a.to_dict()
        item["explanation"] = llm.explain(a)
        output.append(item)
    _print_json(output)


def cmd_summarize(args, config) -> None:
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    summaries = PerformanceAssistService(config).summarize(days, expected_work_days=args.work_days)
    _print_json([s.to_dict() for s in summaries])


def cmd_metrics(args, config) -> None:
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    service = AttendanceMetricsService()
    employee_ids = sorted({d.employee_id for d in days})
    _print_json([service.analyze(emp_id, days).to_dict() for emp_id in employee_ids])


def cmd_notify(args, config) -> None:
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    anomalies = AnomalyEngine(config).detect(days)
    notifications = NotificationService().build_notifications(anomalies)
    _print_json([n.to_dict() for n in notifications])


def cmd_report(args, config) -> None:
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    anomalies = AnomalyEngine(config).detect(days)
    rows = [a.to_dict() for a in anomalies]
    report = ReportService()
    if args.format == "csv":
        print(report.to_csv(rows))
    elif args.format == "markdown":
        print(report.to_markdown_table(rows))
    elif args.format == "html":
        print(report.to_html_page("考勤异常报告", [{"heading": "异常列表", "rows": rows}]))
    else:
        _print_json(rows)


def cmd_monthly_report(args, config) -> None:
    """输出指定月份的考勤结算结果。"""
    records = _load_data(args.data)
    days = AttendanceCleaner().clean(records)
    anomalies = AnomalyEngine(config).detect(days)

    calendar = WorkingCalendar([])
    leave = LeaveService([])
    settlement = MonthlySettlementService(calendar, leave)

    employee_ids = sorted({d.employee_id for d in days})
    results = [
        settlement.settle(emp_id, args.year_month, days, anomalies).to_dict()
        for emp_id in employee_ids
    ]
    _print_json(results)


def main(argv: List[str] | None = None) -> None:
    config = load_config()
    parser = argparse.ArgumentParser(prog="attendance-anomaly", description="考勤异常识别与绩效辅助评估系统")
    parser.add_argument("--data", type=Path, default=config.data_dir / "sample_attendance.json", help="考勤流水 JSON 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("clean", help="清洗流水").set_defaults(func=cmd_clean)

    detect = sub.add_parser("detect", help="识别异常")
    detect.set_defaults(func=cmd_detect)

    summarize = sub.add_parser("summarize", help="绩效辅助摘要")
    summarize.add_argument("--work-days", type=int, default=5, help="考核周期内的应出勤天数")
    summarize.set_defaults(func=cmd_summarize)

    sub.add_parser("metrics", help="出勤衍生指标").set_defaults(func=cmd_metrics)
    sub.add_parser("notify", help="生成异常通知").set_defaults(func=cmd_notify)

    report = sub.add_parser("report", help="导出报告")
    report.add_argument("--format", choices=["json", "csv", "markdown", "html"], default="json")
    report.set_defaults(func=cmd_report)

    monthly = sub.add_parser("monthly-report", help="月度考勤结算")
    monthly.add_argument("--year-month", required=True, help="月份，如 2026-09")
    monthly.set_defaults(func=cmd_monthly_report)

    args = parser.parse_args(argv)
    args.func(args, config)


if __name__ == "__main__":
    main()
