"""配置加载服务。

从 JSON 文件加载班次、节假日、请假申请等业务配置。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from attendance_anomaly.models.holiday import Holiday
from attendance_anomaly.models.leave import LeaveRequest
from attendance_anomaly.models.shift import ShiftType


class ConfigLoader:
    """业务配置加载器。"""

    @staticmethod
    def _read_json(path: Path) -> list:
        return json.loads(path.read_text(encoding="utf-8"))

    def load_shift_types(self, path: Path) -> List[ShiftType]:
        raw = self._read_json(path)
        return [
            ShiftType(
                shift_type_id=item["shift_type_id"],
                name=item["name"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                grace_minutes=item.get("grace_minutes", 5),
                break_minutes=item.get("break_minutes", 60),
            )
            for item in raw
        ]

    def load_holidays(self, path: Path) -> List[Holiday]:
        raw = self._read_json(path)
        return [
            Holiday(date=item["date"], name=item.get("name", ""), is_rest=item.get("is_rest", True))
            for item in raw
        ]

    def load_leave_requests(self, path: Path) -> List[LeaveRequest]:
        raw = self._read_json(path)
        return [
            LeaveRequest(
                request_id=item["request_id"],
                employee_id=item["employee_id"],
                leave_type=item["leave_type"],
                start_date=item["start_date"],
                end_date=item["end_date"],
                status=item.get("status", "approved"),
                reason=item.get("reason", ""),
            )
            for item in raw
        ]
