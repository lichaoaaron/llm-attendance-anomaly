"""法定节假日生成服务。

按年份生成中国法定节假日与调休安排（简化规则），供工作日历初始化使用。
说明：实际放假安排以国务院每年公布为准，此处提供常用节日的近似规则，
用于演示与本地离线使用。
"""
from __future__ import annotations

from datetime import date
from typing import List

from attendance_anomaly.models.holiday import Holiday


class HolidayCalendarService:
    """法定节假日配置生成器。"""

    def generate(self, year: int) -> List[Holiday]:
        """生成指定年份的节假日（含休息日，不含调休上班）。"""
        holidays: List[Holiday] = []

        # 元旦：1 月 1 日。
        holidays.append(Holiday(date(year, 1, 1).isoformat(), "元旦", is_rest=True))

        # 春节：以农历正月初一近似为 2 月前后，简化处理为固定区间。
        # 这里按经验近似（2 月 10 日前后），实际以当年公布为准。
        for offset in range(7):
            holidays.append(
                Holiday(self._date(year, 2, 10 + offset).isoformat(), "春节", is_rest=True)
            )

        # 清明节：4 月 4 日前后。
        holidays.append(Holiday(date(year, 4, 4).isoformat(), "清明节", is_rest=True))

        # 劳动节：5 月 1 日。
        holidays.append(Holiday(date(year, 5, 1).isoformat(), "劳动节", is_rest=True))

        # 端午节：6 月上旬（近似 6 月 1 日 + 农历偏移）。
        holidays.append(Holiday(date(year, 6, 1).isoformat(), "端午节", is_rest=True))

        # 中秋节：9 月中下旬。
        holidays.append(Holiday(date(year, 9, 15).isoformat(), "中秋节", is_rest=True))

        # 国庆节：10 月 1 日 - 7 日。
        for offset in range(7):
            holidays.append(
                Holiday(date(year, 10, 1 + offset).isoformat(), "国庆节", is_rest=True)
            )

        return holidays

    @staticmethod
    def _date(year: int, month: int, day: int) -> date:
        return date(year, month, day)
