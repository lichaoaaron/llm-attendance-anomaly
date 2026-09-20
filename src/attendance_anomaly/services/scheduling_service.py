"""排班管理服务。

按班次类型与轮换规则为员工生成排班表，支持按周轮换与固定班次。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.shift import ShiftAssignment, ShiftType
from attendance_anomaly.utils.time_utils import add_days


@dataclass
class SchedulePlan:
    """一段日期范围内的排班计划。"""

    assignments: List[ShiftAssignment] = field(default_factory=list)

    def to_dict(self) -> dict:
        return [a.to_dict() for a in self.assignments]

    def by_employee(self, employee_id: str) -> List[ShiftAssignment]:
        return [a for a in self.assignments if a.employee_id == employee_id]


class SchedulingService:
    """排班生成服务。"""

    def __init__(self, shift_types: List[ShiftType]) -> None:
        self._types: Dict[str, ShiftType] = {s.shift_type_id: s for s in shift_types}

    def generate_fixed(
        self,
        employee_ids: List[str],
        start_date: str,
        days: int,
        shift_type_id: str,
        rest_weekends: bool = True,
    ) -> SchedulePlan:
        """为员工生成固定班次排班，可选择周末休息。"""
        if shift_type_id not in self._types:
            raise ValueError(f"未知班次类型：{shift_type_id}")

        plan = SchedulePlan()
        for emp_id in employee_ids:
            for offset in range(days):
                date = add_days(start_date, offset)
                if rest_weekends:
                    from attendance_anomaly.utils.time_utils import is_weekend
                    if is_weekend(date):
                        continue
                plan.assignments.append(
                    ShiftAssignment(employee_id=emp_id, date=date, shift_type_id=shift_type_id, required=True)
                )
        return plan

    def generate_rotation(
        self,
        employee_ids: List[str],
        start_date: str,
        days: int,
        shift_type_ids: List[str],
    ) -> SchedulePlan:
        """按天轮换多个班次类型生成排班。"""
        for sid in shift_type_ids:
            if sid not in self._types:
                raise ValueError(f"未知班次类型：{sid}")

        plan = SchedulePlan()
        for offset in range(days):
            date = add_days(start_date, offset)
            shift_type_id = shift_type_ids[offset % len(shift_type_ids)]
            for emp_id in employee_ids:
                plan.assignments.append(
                    ShiftAssignment(employee_id=emp_id, date=date, shift_type_id=shift_type_id, required=True)
                )
        return plan
