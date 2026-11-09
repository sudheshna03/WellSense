"""Ablations computed from the saved nested-CV fold scores (same folds for every model => paired comparisons).
Also a scripted, clearly-labelled demonstration of ranking before vs after feedback (NOT user data).
Usage: python -m src.evaluation.ablation_study"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.recommendations.feedback_adapter import MIN_FEEDBACK
from src.recommendations.recommendation_engine import eligible
from src.recommendations.recommendation_ranker import rank
from src.utils.validation import validate_assessment

ROOT = Path(__file__).resolve().parents[2]
TUNED, INIT = "Tuned MLP (nested CV)", "Initial MLP (32-16, alpha=1e-4)"
CLASSICAL = ["Logistic Regression", "Decision Tree", "Random Forest", "SVM (RBF)", "Gradient Boosting"]


def paired(res, tier_a, model_a, tier_b, model_b, metric="balanced_acc"):
    a = res[(res.tier == tier_a) & (res.model == model_a)].sort_values("fold")[metric].to_numpy()
    b = res[(res.tier == tier_b) & (res.model == model_b)].sort_values("fold")[metric].to_numpy()
    d = a - b
    return {"mean_A": round(a.mean(), 3), "mean_B": round(b.mean(), 3), "mean_diff(A-B)": round(d.mean(), 3),
            "sd_diff": round(d.std(ddof=1), 3), "folds_A_better": int((d > 0).sum()), "folds": len(d)}


def main():
    res = pd.read_csv(ROOT / "results" / "tables" / "cross_validation_results.csv")
    rows = []
    for t in "ABC":
        best = max(CLASSICAL, key=lambda m: res[(res.tier == t) & (res.model == m)].balanced_acc.mean())
        rows.append({"ablation": f"Tuned MLP vs best classical ({best}), tier {t}", **paired(res, t, TUNED, t, best)})
        rows.append({"ablation": f"Regularisation/tuning: tuned vs initial MLP, tier {t}", **paired(res, t, TUNED, t, INIT)})
    rows.append({"ablation": "Feature set: tier B vs tier A (tuned MLP)", **paired(res, "B", TUNED, "A", TUNED)})
    rows.append({"ablation": "Feature set: tier C vs tier B (tuned MLP; C includes likely-leaky treatment)", **paired(res, "C", TUNED, "B", TUNED)})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "results" / "tables" / "ablation_results.csv", index=False)
    print(out.to_string(index=False))

    # Ranking before/after feedback for ONE scripted student (mechanism demonstration only)
    c, _ = validate_assessment(dict(gender="Female", age=20, year=2, cgpa="3.00 - 3.49", course_group="engineering_it",
                                    married=False, anxiety=False, panic=False, sleep_hours=4, social_support=1,
                                    activity_days=0, screen_hours=8))
    cands = eligible(c, {"band": "lower"})
    before = rank(cands)
    after = rank(cands, {"Sleep routine": {"helpful": 0, "not_helpful": MIN_FEEDBACK + 2},
                         "Social connection": {"helpful": 3, "not_helpful": 0}})
    demo = pd.DataFrame({"rank": range(1, len(before) + 1), "before_feedback": [r["rule_id"] for r in before],
                         "after_feedback": [r["rule_id"] for r in after]})
    demo.to_csv(ROOT / "results" / "tables" / "ranking_before_after_scripted_demo.csv", index=False)
    print("\nSCRIPTED DEMO (not real user feedback)\n", demo.to_string(index=False))


if __name__ == "__main__":
    main()
