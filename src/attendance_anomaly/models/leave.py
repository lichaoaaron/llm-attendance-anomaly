"""请假数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LeaveRequest:
    """一条请假/出差/调休申请。"""

    request_id: str
    employee_id: str
    leave_type: str          # annual / sick / personal / travel / comp
    start_date: str          # YYYY-MM-DD
    end_date: str            # YYYY-MM-DD（含）
    status: str = "approved"  # pending / approved / rejected
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "employee_id": self.employee_id,
            "leave_type": self.leave_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass
class LeaveConflict:
    """请假与考勤记录的冲突。"""

    employee_id: str
    date: str
    leave_type: str
    detail: str

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "date": self.date,
            "leave_type": self.leave_type,
            "detail": self.detail,
        }


# 请假类型到中文名称的映射。
LEAVE_TYPE_LABELS = {
    "annual": "年假",
    "sick": "病假",
    "personal": "事假",
    "travel": "出差",
    "comp": "调休",
}
