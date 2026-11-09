"""Phase 2-3 experiments: fair comparison of baselines and MLP with repeated stratified CV.

Every model sees identical folds. Models with a hyper-parameter grid are tuned by an INNER
3-fold CV on the training fold only (nested CV), so the outer score is an unbiased estimate.
Usage: python -m src.models.run_experiments
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score, accuracy_score
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.data.preprocessing import SEED, TIERS, build_preprocessor, load_clean

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
N_SPLITS, N_REPEATS = 5, 5  # 25 outer folds


def model_zoo():
    mlp = lambda **k: MLPClassifier(solver="adam", max_iter=600, random_state=SEED, **k)
    return {
        "Dummy (majority)": (DummyClassifier(strategy="most_frequent"), None, "Baseline"),
        "Logistic Regression": (LogisticRegression(class_weight="balanced", max_iter=1000),
                                {"clf__C": [0.01, 0.1, 1, 10]}, "ML"),
        "Decision Tree": (DecisionTreeClassifier(class_weight="balanced", random_state=SEED),
                          {"clf__max_depth": [2, 3, 5]}, "ML"),
        "Random Forest": (RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=SEED),
                          {"clf__max_depth": [3, 5, None]}, "ML"),
        "SVM (RBF)": (SVC(class_weight="balanced", probability=True, random_state=SEED),
                      {"clf__C": [0.1, 1, 10]}, "ML"),
        "Gradient Boosting": (GradientBoostingClassifier(random_state=SEED),
                              {"clf__max_depth": [1, 2], "clf__n_estimators": [50, 150]}, "ML"),
        "Initial MLP (32-16, alpha=1e-4)": (mlp(hidden_layer_sizes=(32, 16), alpha=1e-4), None, "DL"),
        "Tuned MLP (nested CV)": (mlp(hidden_layer_sizes=(32, 16)),
                                  {"clf__hidden_layer_sizes": [(8,), (16,), (32, 16)],
                                   "clf__alpha": [1e-3, 1e-2, 1e-1, 1.0],
                                   # iteration budget chosen by inner CV (sklearn's built-in early stopping
                                   # holds out ~6 rows here, which is too noisy and caused under-training)
                                   "clf__max_iter": [200, 600]}, "Improved DL"),
    }


def score(y, proba, pred):
    return {"accuracy": accuracy_score(y, pred), "balanced_acc": balanced_accuracy_score(y, pred),
            "f1": f1_score(y, pred, zero_division=0),
            "roc_auc": roc_auc_score(y, proba) if len(set(y)) > 1 else np.nan}


def run_tier(tier: str, X, y) -> pd.DataFrame:
    feats = TIERS[tier]
    Xt = X[feats]
    outer = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
    rows = []
    for fold, (tr, te) in enumerate(outer.split(Xt, y)):
        for name, (est, grid, kind) in model_zoo().items():
            pipe = Pipeline([("prep", build_preprocessor(feats)), ("clf", est)])
            if grid:
                pipe = GridSearchCV(pipe, grid, scoring="balanced_accuracy", refit=True,
                                    cv=StratifiedKFold(3, shuffle=True, random_state=SEED))
            pipe.fit(Xt.iloc[tr], y.iloc[tr])
            proba = pipe.predict_proba(Xt.iloc[te])[:, 1]
            pred = pipe.predict(Xt.iloc[te])
            rows.append({"tier": tier, "model": name, "kind": kind, "fold": fold,
                         **score(y.iloc[te], proba, pred)})
    return pd.DataFrame(rows)


def main():
    X, y = load_clean()
    res = pd.concat([run_tier(t, X, y) for t in TIERS], ignore_index=True)
    tables = ROOT / "results" / "tables"; tables.mkdir(parents=True, exist_ok=True)
    res.to_csv(tables / "cross_validation_results.csv", index=False)

    metrics = ["accuracy", "balanced_acc", "f1", "roc_auc"]
    g = res.groupby(["tier", "model", "kind"], sort=False)[metrics]
    summ = g.mean().round(3).join(g.std().round(3), rsuffix="_sd").reset_index()
    summ.to_csv(tables / "model_comparison.csv", index=False)
    print(summ.to_string(index=False))

    # Paired comparison of Tuned MLP against the best classical model per tier (same folds)
    notes = {}
    for t in TIERS:
        d = res[res.tier == t].pivot(index="fold", columns="model", values="balanced_acc")
        ml = [m for m in d.columns if m not in ("Dummy (majority)", "Initial MLP (32-16, alpha=1e-4)", "Tuned MLP (nested CV)")]
        best = d[ml].mean().idxmax()
        diff = d["Tuned MLP (nested CV)"] - d[best]
        notes[t] = {"best_classical": best, "mean_diff_bal_acc(MLP-best)": round(diff.mean(), 3),
                    "folds_mlp_better": int((diff > 0).sum()), "folds": int(len(diff))}
    (ROOT / "results" / "experiment_summary.json").write_text(json.dumps(
        {"seed": SEED, "cv": f"{N_SPLITS}x{N_REPEATS} repeated stratified", "paired_vs_best_classical": notes}, indent=2))
    print(json.dumps(notes, indent=2))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    for ax, t in zip(axes, TIERS):
        s = summ[summ.tier == t]
        ax.barh(s.model, s.balanced_acc, xerr=s.balanced_acc_sd, color="#4C72B0")
        ax.axvline(0.5, color="grey", ls="--"); ax.set_title(f"Feature tier {t}"); ax.set_xlabel("Balanced accuracy (mean ± SD)")
    fig.tight_layout(); fig.savefig(ROOT / "results" / "figures" / "model_comparison.png", dpi=150)


if __name__ == "__main__":
    main()
