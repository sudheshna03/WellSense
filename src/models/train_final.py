"""Fit the final deployed model (tuned MLP, feature tier B) on all data and save the artifact.

Selection note (honest): in nested CV the tuned MLP and the best classical model are statistically tied
(see results/experiment_summary.json). Because the project's research objective is a deep-learning
model and no classical model is reliably better, the MLP is deployed. This is a documented project
decision, not a performance claim.
Usage: python -m src.models.train_final
"""
from __future__ import annotations

import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

from src.data.preprocessing import SEED, TIERS, build_preprocessor, load_clean
from src.models.run_experiments import model_zoo

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
VERSION = "wellsense-mlp-v1"


def _reference(X: pd.DataFrame) -> dict:
    """Typical value per feature (median for numeric/ordinal, mode otherwise). Summary only; no raw rows stored."""
    ref = {}
    for c in X.columns:
        ref[c] = float(X[c].median()) if c in ("age", "year", "cgpa_ord") else X[c].mode().iloc[0]
    return ref


def train(save_path: Path | None = None, tune: bool = True) -> dict:
    X, y = load_clean()
    feats = TIERS["B"]
    est, grid, _ = model_zoo()["Tuned MLP (nested CV)"]
    pipe = Pipeline([("prep", build_preprocessor(feats)), ("clf", est)])
    if tune:
        search = GridSearchCV(pipe, grid, scoring="balanced_accuracy", refit=True,
                              cv=StratifiedKFold(5, shuffle=True, random_state=SEED))
        search.fit(X[feats], y)
        pipe, params, inner = search.best_estimator_, search.best_params_, float(search.best_score_)
    else:
        pipe.fit(X[feats], y)
        params, inner = {}, None
    cv_est = None
    mc = ROOT / "results" / "tables" / "model_comparison.csv"
    if mc.exists():
        t = pd.read_csv(mc)
        row = t[(t.tier == "B") & (t.model == "Tuned MLP (nested CV)")]
        if len(row):
            cv_est = {"balanced_acc": float(row.balanced_acc.iloc[0]), "sd": float(row.balanced_acc_sd.iloc[0])}
    art = {"pipeline": pipe, "features": feats, "version": VERSION, "best_params": {k: str(v) for k, v in params.items()},
           "inner_cv_balanced_acc": inner, "nested_cv_estimate": cv_est, "reference": _reference(X[feats]),
           "n_train": int(len(X)), "seed": SEED}
    out = save_path or (ROOT / "models" / "dl" / "wellsense_mlp_v1.joblib")
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(art, out)
    return art


if __name__ == "__main__":
    a = train()
    print("saved", VERSION, a["best_params"], "nested-CV estimate:", a["nested_cv_estimate"])
