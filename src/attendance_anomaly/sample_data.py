"""示例考勤数据生成器。

按参数生成具有结构特征的示例打卡流水，用于功能演示与测试。
"""
from __future__ import annotations

import random
from typing import List, Optional

from attendance_anomaly.models.attendance import PunchRecord
from attendance_anomaly.utils.time_utils import add_days, to_hhmm


class SampleAttendanceGenerator:
    """示例打卡流水生成器。"""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, employee_ids: List[str], start_date: str, days: int) -> List[PunchRecord]:
        """为若干员工生成 days 天的打卡流水。"""
        records: List[PunchRecord] = []
        for emp_id in employee_ids:
            for offset in range(days):
                date = add_days(start_date, offset)
                # 以一定概率缺卡。
                if self._rng.random() < 0.1:
                    records.append(PunchRecord(emp_id, date, to_hhmm(9 * 60 + self._rng.randint(0, 20)), "in"))
                    continue

                # 正常打卡，偶尔迟到/早退。
                in_minutes = 9 * 60 + self._rng.randint(-5, 40)
                out_minutes = 18 * 60 + self._rng.randint(-30, 60)
                records.append(PunchRecord(emp_id, date, to_hhmm(in_minutes), "in"))
                records.append(PunchRecord(emp_id, date, to_hhmm(out_minutes), "out"))
        return records

    def generate_with_overtime(self, employee_ids: List[str], start_date: str, days: int) -> List[PunchRecord]:
        """生成包含较多加班场景的流水。"""
        records = self.generate(employee_ids, start_date, days)
        for emp_id in employee_ids:
            if self._rng.random() < 0.5:
                date = add_days(start_date, self._rng.randint(0, days - 1))
                records.append(PunchRecord(emp_id, date, "09:00", "in"))
                records.append(PunchRecord(emp_id, date, "20:30", "out"))
        return records
