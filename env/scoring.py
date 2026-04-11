from __future__ import annotations

SCORE_EPSILON = 0.001


def clamp_open_unit_interval(value: float) -> float:
    return max(SCORE_EPSILON, min(1.0 - SCORE_EPSILON, value))
