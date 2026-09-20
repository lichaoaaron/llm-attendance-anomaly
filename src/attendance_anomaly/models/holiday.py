"""节假日与工作日历数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Holiday:
    """法定节假日或特殊休息日。"""

    date: str              # YYYY-MM-DD
    name: str
    is_rest: bool = True   # True=休息日，False=调休上班日

    def to_dict(self) -> dict:
        return {"date": self.date, "name": self.name, "is_rest": self.is_rest}


class WorkingCalendar:
    """工作日历：结合节假日与调休判定某天是否为工作日。"""

    def __init__(self, holidays: List[Holiday]) -> None:
        self._holiday_map: Dict[str, Holiday] = {h.date: h for h in holidays}

    def is_workday(self, date_str: str) -> bool:
        """判断某天是否为工作日（优先看节假日/调休配置，再看周末）。"""
        holiday = self._holiday_map.get(date_str)
        if holiday is not None:
            # 调休上班日（is_rest=False）覆盖周末，视为工作日。
            return not holiday.is_rest
        from attendance_anomaly.utils.time_utils import is_weekend
        return not is_weekend(date_str)

    def is_holiday(self, date_str: str) -> bool:
        """判断某天是否为休息日（节假日或周末）。"""
        return not self.is_workday(date_str)

    def holiday_name(self, date_str: str) -> str:
        """返回该日节假日名称，非节假日返回空串。"""
        holiday = self._holiday_map.get(date_str)
        if holiday is not None and holiday.is_rest:
            return holiday.name
        return ""
