"""Build personalised recommendations from validated answers and the model result."""
from __future__ import annotations

from src.recommendations.recommendation_ranker import rank
from src.recommendations.recommendation_rules import RULES


def eligible(clean: dict, prediction: dict) -> list[dict]:
    cands = []
    for r in RULES:
        res = r["fn"](clean, prediction)
        if res is None:
            continue
        strength, reason = res
        cands.append({"rule_id": r["id"], "category": r["category"], "title": r["title"],
                      "description": r["description"], "action": r["action"], "minutes": r["minutes"],
                      "difficulty": r["difficulty"], "safety": r.get("safety", False),
                      "reason": reason, "strength": round(float(strength), 3)})
    # the generic fallback only appears when nothing specific applies
    specific = [c for c in cands if c["rule_id"] != "routine_basics"]
    return specific or cands


def recommend(clean: dict, prediction: dict, category_stats: dict | None = None, top_k: int = 6) -> list[dict]:
    return rank(eligible(clean, prediction), category_stats, top_k)
