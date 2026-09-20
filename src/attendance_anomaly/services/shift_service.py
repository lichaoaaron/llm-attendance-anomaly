"""班次管理服务。

按班次安排判定员工出勤是否异常，支持跨天夜班、弹性宽限与休息时长扣除。
"""
from __future__ import annotations

from typing import Dict, List, Optional

from attendance_anomaly.models.attendance import AttendanceDay
from attendance_anomaly.models.shift import ShiftAssignment, ShiftResult, ShiftType
from attendance_anomaly.utils.time_utils import duration_minutes, to_minutes


class ShiftService:
    """班次判定服务。"""

    def __init__(self, shift_types: List[ShiftType]) -> None:
        self._types: Dict[str, ShiftType] = {s.shift_type_id: s for s in shift_types}

    def evaluate(
        self,
        assignment: ShiftAssignment,
        day: Optional[AttendanceDay],
    ) -> ShiftResult:
        """按班次安排评估某员工某天的出勤情况。"""
        shift = self._types.get(assignment.shift_type_id)
        if shift is None:
            raise ValueError(f"未知班次类型：{assignment.shift_type_id}")

        result = ShiftResult(
            employee_id=assignment.employee_id,
            date=assignment.date,
            shift_type_id=assignment.shift_type_id,
            shift_name=shift.name,
        )
        if not assignment.required:
            # 无需出勤（请假/调休），不判定异常。
            return result

        if day is None or day.first_in is None or day.last_out is None:
            result.anomalies.append("缺卡：未记录到完整打卡")
            return result

        result.first_in = day.first_in
        result.last_out = day.last_out

        # 迟到判定：首次进入晚于班次开始时间 + 宽限。
        late_threshold = to_minutes(shift.start_time) + shift.grace_minutes
        first_in_min = to_minutes(day.first_in)
        if first_in_min > late_threshold:
            result.anomalies.append("迟到")

        # 早退判定：最后离开早于班次结束时间 - 宽限（跨天班次特殊处理）。
        if self._cross_day_early_leave(day.last_out, shift.end_time, shift.grace_minutes):
            result.anomalies.append("早退")

        # 实际工作时长 = 在岗时长 - 休息时长。
        worked = day.work_hours * 60 - shift.break_minutes
        expected = duration_minutes(shift.start_time, shift.end_time) - shift.break_minutes
        result.actual_hours = max(0.0, worked / 60.0)
        result.expected_hours = expected / 60.0

        # 加班判定：实际超过期望时长。
        if worked > expected + 60:
            result.anomalies.append("加班")

        return result

    @staticmethod
    def _cross_day_early_leave(last_out: str, end_time: str, grace_minutes: int) -> bool:
        """早退判定：离开时间早于班次结束时间减去宽限。"""
        end_min = to_minutes(end_time)
        out_min = to_minutes(last_out)
        return out_min < end_min - grace_minutes
