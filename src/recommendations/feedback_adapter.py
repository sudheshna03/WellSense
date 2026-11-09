"""Feedback-driven adaptation of recommendation RANKING (never of the prediction model).

Transparent rule: per student and category, multiplier = 1 + 0.6 * (helpful - not_helpful) / (helpful + not_helpful + 2),
applied only once at least MIN_FEEDBACK helpful/not-helpful votes exist, clamped to [FLOOR, CEIL].
The floor keeps every category recoverable; 'not tried' carries no signal. Safety rules are never suppressed.
"""
from __future__ import annotations

MIN_FEEDBACK = 2
FLOOR, CEIL = 0.5, 1.5
EXPLORE_BONUS = 0.05


def category_multiplier(stats: dict | None) -> float:
    if not stats:
        return 1.0
    h, n = stats.get("helpful", 0), stats.get("not_helpful", 0)
    if h + n < MIN_FEEDBACK:
        return 1.0
    return max(FLOOR, min(CEIL, 1 + 0.6 * (h - n) / (h + n + 2)))


def multipliers(category_stats: dict[str, dict]) -> dict[str, float]:
    return {c: category_multiplier(s) for c, s in (category_stats or {}).items()}
