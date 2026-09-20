"""考勤异常识别引擎。

在清洗后的每日出勤汇总上，按规则识别四类异常：
- late：上班晚于标准时间且超过宽限；
- early_leave：下班早于标准时间且超过宽限；
- missing_punch：缺打卡（无进入或无离开记录）；
- overtime：当日工作时长超过加班阈值。
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from attendance_anomaly.config import AppConfig
from attendance_anomaly.models.attendance import Anomaly, AttendanceDay

_TIME_FMT = "%H:%M"


def _to_minutes(time_str: str) -> int:
    t = datetime.strptime(time_str, _TIME_FMT)
    return t.hour * 60 + t.minute


class AnomalyEngine:
    """考勤异常规则引擎。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def detect(self, days: List[AttendanceDay]) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        for day in days:
            anomalies.extend(self._detect_day(day))
        return anomalies

    def _detect_day(self, day: AttendanceDay) -> List[Anomaly]:
        cfg = self.config
        result: List[Anomaly] = []

        # 缺卡判断。
        if day.first_in is None or day.last_out is None:
            result.append(
                Anomaly(
                    employee_id=day.employee_id,
                    date=day.date,
                    anomaly_type="missing_punch",
                    severity="medium",
                    detail="存在缺卡：未记录到完整进入/离开打卡",
                )
            )
            return result

        # 迟到判断。
        late_minutes = _to_minutes(day.first_in) - cfg.start_minutes
        if late_minutes > cfg.late_grace_minutes:
            result.append(
                Anomaly(
                    employee_id=day.employee_id,
                    date=day.date,
                    anomaly_type="late",
                    severity=self._severity(late_minutes),
                    detail=f"迟到 {late_minutes} 分钟",
                )
            )

        # 早退判断。
        early_minutes = cfg.end_minutes - _to_minutes(day.last_out)
        if early_minutes > cfg.early_grace_minutes:
            result.append(
                Anomaly(
                    employee_id=day.employee_id,
                    date=day.date,
                    anomaly_type="early_leave",
                    severity=self._severity(early_minutes),
                    detail=f"早退 {early_minutes} 分钟",
                )
            )

        # 加班判断。
        if day.work_hours > cfg.overtime_hours:
            result.append(
                Anomaly(
                    employee_id=day.employee_id,
                    date=day.date,
                    anomaly_type="overtime",
                    severity="low",
                    detail=f"工作时长 {day.work_hours} 小时，超过加班阈值",
                )
            )

        return result

    @staticmethod
    def _severity(minutes: int) -> str:
        """根据超时分钟数判断严重程度。"""
        if minutes >= 60:
            return "high"
        if minutes >= 30:
            return "medium"
        return "low"
