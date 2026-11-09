"""Confusion matrix (out-of-fold, tuned-MLP configuration) and MLP training-loss curve.
Usage: python -m src.evaluation.generate_figures"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.metrics import ConfusionMatrixDisplay, balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from src.data.preprocessing import SEED, load_clean
from src.models.predict import load_artifact

ROOT = Path(__file__).resolve().parents[2]
art = load_artifact(); X, y = load_clean(); X = X[art["features"]]
pred = cross_val_predict(clone(art["pipeline"]), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED))
fig, ax = plt.subplots(figsize=(4, 3.6))
ConfusionMatrixDisplay.from_predictions(y, pred, display_labels=["No", "Yes"], ax=ax, colorbar=False)
ax.set_title(f"Out-of-fold confusion matrix\n(bal. acc. {balanced_accuracy_score(y, pred):.2f}, single 5-fold run)")
fig.tight_layout(); fig.savefig(ROOT / "results/figures/confusion_matrix.png", dpi=150)
fig, ax = plt.subplots(figsize=(5, 3.5))
ax.plot(art["pipeline"].named_steps["clf"].loss_curve_)
ax.set(xlabel="Epoch", ylabel="Training loss", title="Final MLP training loss (no validation curve: early stopping off)")
fig.tight_layout(); fig.savefig(ROOT / "results/figures/ann_training_curve.png", dpi=150)
