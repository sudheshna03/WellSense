"""Explanations for the deployed MLP.

SHAP cannot be installed in this environment, so two model-agnostic methods are used:
- global: out-of-fold permutation importance (see global_explanation.py)
- local: occlusion - replace one answer with a typical value and measure the change in the model estimate.
Both describe the MODEL's behaviour. They are associations, not causes.
"""
from __future__ import annotations

import copy

from src.models.predict import load_artifact, to_frame

DISPLAY = {
    "gender_female": "Gender", "age": "Age", "year": "Year of study", "cgpa_ord": "CGPA band",
    "married": "Marital status", "course_group": "Course group", "anxiety": "Self-reported anxiety",
    "panic": "Self-reported panic attacks", "treatment": "Sought specialist treatment",
}

CAVEAT = ("These are associations learned by a statistical model from a small student survey. They do not show "
          "that any factor caused the result, and this is not a diagnosis.")


def local_explanation(clean: dict, artifact: dict | None = None, min_effect: float = 0.01) -> list[dict]:
    art = artifact or load_artifact()
    pipe, feats, ref = art["pipeline"], art["features"], art["reference"]
    X = to_frame(clean, feats)
    base = float(pipe.predict_proba(X)[0, 1])
    out = []
    for f in feats:
        Xr = X.copy()
        Xr[f] = ref[f]
        eff = base - float(pipe.predict_proba(Xr)[0, 1])  # >0: this answer raises the estimate vs a typical answer
        if abs(eff) < min_effect:
            continue
        out.append({"feature": f, "name": DISPLAY.get(f, f), "effect": round(eff, 3),
                    "direction": "raises" if eff > 0 else "lowers",
                    "text": (f"{DISPLAY.get(f, f)}: your answer {'raised' if eff > 0 else 'lowered'} the model's "
                             f"estimate by about {abs(eff) * 100:.0f} percentage points compared with a typical answer.")})
    return sorted(out, key=lambda d: -abs(d["effect"]))


def consistency_check(clean: dict, artifact: dict | None = None) -> float:
    """Sum of occlusion effects vs. total shift to the all-typical profile; used in tests to check wiring."""
    art = artifact or load_artifact()
    X = to_frame(clean, art["features"])
    return float(art["pipeline"].predict_proba(X)[0, 1])
