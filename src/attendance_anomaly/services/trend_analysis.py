"""考勤趋势分析服务。

对多周期考勤数据做趋势对比，识别迟到率、加班时长的周度变化，
输出趋势方向与异常波动提示。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly, AttendanceDay
from attendance_anomaly.utils.statistics import mean


@dataclass
class TrendPoint:
    """某个周期的考勤指标点。"""

    period: str
    present_days: int
    anomaly_count: int
    late_count: int
    avg_work_hours: float

    def to_dict(self) -> dict:
        return {
            "period": self.period,
            "present_days": self.present_days,
            "anomaly_count": self.anomaly_count,
            "late_count": self.late_count,
            "avg_work_hours": round(self.avg_work_hours, 2),
        }


@dataclass
class TrendReport:
    """趋势分析报告。"""

    points: List[TrendPoint] = field(default_factory=list)
    late_trend: str = "stable"
    overtime_trend: str = "stable"

    def to_dict(self) -> dict:
        return {
            "points": [p.to_dict() for p in self.points],
            "late_trend": self.late_trend,
            "overtime_trend": self.overtime_trend,
        }


class TrendAnalysisService:
    """考勤趋势分析。"""

    def analyze(
        self,
        periods: List[str],
        days: List[AttendanceDay],
        anomalies: List[Anomaly],
    ) -> TrendReport:
        """按给定周期列表（如 ['2026-09-14','2026-09-21'] 表示周起始）生成趋势。"""
        points: List[TrendPoint] = []
        for i, start in enumerate(periods):
            end = periods[i + 1] if i + 1 < len(periods) else None
            point = self._point_for_period(start, end, days, anomalies)
            points.append(point)

        report = TrendReport(points=points)
        if len(points) >= 2:
            report.late_trend = self._trend([p.late_count for p in points])
            report.overtime_trend = self._trend([p.avg_work_hours for p in points])
        return report

    def _point_for_period(self, start: str, end: str | None, days: List[AttendanceDay], anomalies: List[Anomaly]) -> TrendPoint:
        period_days = [
            d for d in days
            if d.date >= start and (end is None or d.date < end)
        ]
        period_anomalies = [
            a for a in anomalies
            if a.date >= start and (end is None or a.date < end)
        ]
        present = sum(1 for d in period_days if d.first_in is not None and d.last_out is not None)
        late = sum(1 for a in period_anomalies if a.anomaly_type == "late")
        hours = [d.work_hours for d in period_days]
        return TrendPoint(
            period=start,
            present_days=present,
            anomaly_count=len(period_anomalies),
            late_count=late,
            avg_work_hours=mean(hours),
        )

    @staticmethod
    def _trend(values: List[float]) -> str:
        """判断序列趋势：整体上升/下降/稳定。"""
        if len(values) < 2:
            return "stable"
        first_half = mean(values[: len(values) // 2])
        second_half = mean(values[len(values) // 2:])
        delta = second_half - first_half
        if delta > 0.5:
            return "rising"
        if delta < -0.5:
            return "falling"
        return "stable"
