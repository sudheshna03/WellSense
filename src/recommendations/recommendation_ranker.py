"""Rank eligible recommendations: score = need strength x feedback multiplier (+ small exploration bonus)."""
from __future__ import annotations

from src.recommendations.feedback_adapter import EXPLORE_BONUS, category_multiplier


def rank(candidates: list[dict], category_stats: dict[str, dict] | None = None, top_k: int = 6) -> list[dict]:
    stats = category_stats or {}
    any_feedback = any(s.get("helpful", 0) + s.get("not_helpful", 0) > 0 for s in stats.values())
    out = []
    for c in candidates:
        m = category_multiplier(stats.get(c["category"]))
        s = c["strength"] * m
        if any_feedback and c["category"] not in stats:
            s += EXPLORE_BONUS  # keep variety: gently surface categories not yet rated
        if c.get("safety"):
            s += 10.0  # safety-relevant support is always shown first and never suppressed
        out.append({**c, "feedback_multiplier": round(m, 3), "ranking_score": round(s, 3)})
    out.sort(key=lambda d: -d["ranking_score"])
    return out[:top_k]
