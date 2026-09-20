"""示例数据加载器。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from attendance_anomaly.models.attendance import PunchRecord


def load_punches(path: Path) -> List[PunchRecord]:
    """从 JSON 文件加载原始打卡流水。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        PunchRecord(
            employee_id=item["employee_id"],
            date=item["date"],
            punch_time=item["punch_time"],
            punch_type=item["punch_type"],
        )
        for item in raw
    ]
