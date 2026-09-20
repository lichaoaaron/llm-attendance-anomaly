"""考勤流水导入服务。

从 CSV 文本导入打卡流水，包含字段校验与类型转换。
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from attendance_anomaly.models.attendance import PunchRecord


@dataclass
class ImportResult:
    """导入结果。"""

    records: List[PunchRecord] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_rows: int = 0

    def to_dict(self) -> dict:
        return {"imported": len(self.records), "errors": self.errors, "total_rows": self.total_rows}


class PunchImporter:
    """打卡流水 CSV 导入器。"""

    def __init__(self) -> None:
        self._column_map: Dict[str, str] = {
            "员工编号": "employee_id",
            "日期": "date",
            "打卡时间": "punch_time",
            "打卡类型": "punch_type",
        }

    def import_csv(self, text: str) -> ImportResult:
        result = ImportResult()
        reader = csv.DictReader(self._lines(text))
        if not reader.fieldnames:
            result.errors.append("CSV 缺少表头")
            return result

        for row_index, raw_row in enumerate(reader, start=2):
            result.total_rows += 1
            row = {self._column_map.get(k, k): v for k, v in raw_row.items() if k}
            record, error = self._parse_row(row, row_index)
            if error:
                result.errors.append(error)
            else:
                result.records.append(record)
        return result

    def _parse_row(self, row: Dict[str, str], row_index: int) -> tuple[Optional[PunchRecord], str]:
        required = ["employee_id", "date", "punch_time", "punch_type"]
        missing = [f for f in required if not (row.get(f) or "").strip()]
        if missing:
            return None, f"第 {row_index} 行缺少必填字段：{', '.join(missing)}"

        punch_type = row["punch_type"].strip()
        if punch_type not in ("in", "out"):
            return None, f"第 {row_index} 行打卡类型非法：{punch_type}"

        return (
            PunchRecord(
                employee_id=row["employee_id"].strip(),
                date=row["date"].strip(),
                punch_time=row["punch_time"].strip(),
                punch_type=punch_type,
            ),
            "",
        )

    @staticmethod
    def _lines(text: str) -> list[str]:
        return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
