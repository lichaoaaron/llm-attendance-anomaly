"""时间工具与统计工具单元测试。"""
from __future__ import annotations

import unittest

from attendance_anomaly.utils.statistics import frequency_distribution, mean, median, percentile, stddev
from attendance_anomaly.utils.time_utils import (
    add_days,
    duration_minutes,
    is_weekend,
    overlaps,
    to_hhmm,
    to_minutes,
)


class TestTimeUtils(unittest.TestCase):
    def test_to_minutes(self) -> None:
        self.assertEqual(to_minutes("09:30"), 570)
        self.assertEqual(to_minutes("18:00"), 1080)

    def test_to_hhmm(self) -> None:
        self.assertEqual(to_hhmm(570), "09:30")
        self.assertEqual(to_hhmm(25 * 60), "01:00")

    def test_duration_minutes(self) -> None:
        self.assertEqual(duration_minutes("09:00", "18:00"), 540)

    def test_duration_cross_day(self) -> None:
        self.assertEqual(duration_minutes("22:00", "06:00"), 480)

    def test_overlaps(self) -> None:
        self.assertTrue(overlaps("09:00", "12:00", "11:00", "13:00"))
        self.assertFalse(overlaps("09:00", "10:00", "10:00", "11:00"))

    def test_is_weekend(self) -> None:
        self.assertFalse(is_weekend("2026-09-14"))  # 周一
        self.assertTrue(is_weekend("2026-09-19"))   # 周六

    def test_add_days(self) -> None:
        self.assertEqual(add_days("2026-09-14", 2), "2026-09-16")


class TestStatistics(unittest.TestCase):
    def test_mean_median(self) -> None:
        self.assertEqual(mean([1, 2, 3]), 2.0)
        self.assertEqual(median([1, 2, 3]), 2.0)

    def test_stddev(self) -> None:
        self.assertAlmostEqual(stddev([1, 1, 1]), 0.0)

    def test_percentile(self) -> None:
        self.assertEqual(percentile([1.0, 2.0, 3.0], 50), 2.0)

    def test_frequency(self) -> None:
        self.assertEqual(frequency_distribution(["a", "b", "a"]), {"a": 2, "b": 1})


if __name__ == "__main__":
    unittest.main()
