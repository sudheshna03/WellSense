"""Global explanation: out-of-fold permutation importance of the deployed MLP configuration.
Usage: python -m src.explainability.global_explanation"""
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RepeatedStratifiedKFold

from src.data.preprocessing import SEED, load_clean
from src.explainability.explainer import DISPLAY
from src.models.predict import load_artifact

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]


def compute(n_repeats: int = 20) -> pd.DataFrame:
    art = load_artifact()
    feats = art["features"]
    X, y = load_clean()
    X = X[feats]
    rows = []
    for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEED).split(X, y):
        m = clone(art["pipeline"]).fit(X.iloc[tr], y.iloc[tr])  # same hyper-parameters, refit on train fold
        r = permutation_importance(m, X.iloc[te], y.iloc[te], scoring="balanced_accuracy",
                                   n_repeats=n_repeats, random_state=SEED)
        rows.append(pd.Series(r.importances_mean, index=feats))
    d = pd.concat(rows, axis=1)
    out = pd.DataFrame({"feature": [DISPLAY[f] for f in feats], "importance": d.mean(axis=1).values,
                        "sd_across_folds": d.std(axis=1).values}).sort_values("importance", ascending=False)
    return out.round(4)


def main():
    out = compute()
    (ROOT / "results" / "tables").mkdir(parents=True, exist_ok=True)
    out.to_csv(ROOT / "results" / "tables" / "global_importance.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    o = out.iloc[::-1]
    ax.barh(o.feature, o.importance, xerr=o.sd_across_folds, color="#4C72B0")
    ax.set(xlabel="Drop in balanced accuracy when the feature is shuffled (held-out folds)",
           title="Global feature importance (association, not causation)")
    fig.tight_layout(); fig.savefig(ROOT / "results" / "figures" / "feature_importance.png", dpi=150)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
