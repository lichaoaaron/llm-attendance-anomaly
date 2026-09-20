"""统计工具（考勤场景）。"""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, Sequence


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def stddev(values: Sequence[float], sample: bool = True) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    denominator = len(values) - 1 if sample else len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / denominator)


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    rank = (p / 100.0) * (len(sorted_values) - 1)
    lower = int(rank)
    frac = rank - lower
    if lower + 1 >= len(sorted_values):
        return sorted_values[lower]
    return sorted_values[lower] * (1 - frac) + sorted_values[lower + 1] * frac


def frequency_distribution(values: Iterable[str]) -> dict[str, int]:
    counter = Counter(values)
    return dict(counter.most_common())


def sum_float(values: Iterable[float]) -> float:
    return sum(values)
