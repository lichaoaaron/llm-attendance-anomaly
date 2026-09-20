"""考勤流水清洗服务。

原始打卡数据往往存在重复打卡、乱序、缺卡等问题，本服务负责把流水按
「员工 + 日期」分组，去重、按时间排序，并配对出当天的首次进入与末次
离开，估算当日工作时长。
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from attendance_anomaly.models.attendance import AttendanceDay, PunchRecord

_TIME_FMT = "%H:%M"


def _to_minutes(time_str: str) -> int:
    """把 HH:MM 转换为当天分钟数。"""
    t = datetime.strptime(time_str, _TIME_FMT)
    return t.hour * 60 + t.minute


class AttendanceCleaner:
    """负责把原始打卡流水整理成每日出勤汇总。"""

    def clean(self, records: List[PunchRecord]) -> List[AttendanceDay]:
        grouped: Dict[str, List[PunchRecord]] = defaultdict(list)
        for rec in records:
            grouped[(rec.employee_id, rec.date)].append(rec)

        days: List[AttendanceDay] = []
        for (employee_id, date), punches in grouped.items():
            # 去重：同一人同一天同一时间同一类型只保留一次。
            seen = set()
            unique: List[PunchRecord] = []
            for p in punches:
                key = (p.punch_time, p.punch_type)
                if key not in seen:
                    seen.add(key)
                    unique.append(p)
            # 按时间排序。
            unique.sort(key=lambda p: _to_minutes(p.punch_time))

            first_in = None
            last_out = None
            work_minutes = 0
            # 配对进入/离开，累加在岗时长。
            open_in = None
            for p in unique:
                if p.punch_type == "in":
                    open_in = _to_minutes(p.punch_time)
                    if first_in is None:
                        first_in = p.punch_time
                elif p.punch_type == "out" and open_in is not None:
                    work_minutes += _to_minutes(p.punch_time) - open_in
                    open_in = None
                    last_out = p.punch_time

            days.append(
                AttendanceDay(
                    employee_id=employee_id,
                    date=date,
                    first_in=first_in,
                    last_out=last_out,
                    work_hours=round(work_minutes / 60.0, 2),
                )
            )
        # 按员工、日期排序，便于输出稳定。
        days.sort(key=lambda d: (d.employee_id, d.date))
        return days
