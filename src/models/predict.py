"""Load the saved model artifact and produce a prediction from validated answers."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.data.preprocessing import CGPA_ORDER

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = ROOT / "models" / "dl" / "wellsense_mlp_v1.joblib"


@lru_cache(maxsize=4)
def _load(path: str) -> dict:
    return joblib.load(path)


def load_artifact(path: Path | str | None = None) -> dict:
    p = Path(path or ARTIFACT_PATH)
    if not p.exists():
        raise FileNotFoundError(f"Model artifact not found at {p}. Run: python -m src.models.train_final")
    return _load(str(p))


def to_frame(clean: dict, features: list[str]) -> pd.DataFrame:
    """Build a one-row frame with the exact training column names/order."""
    row = {
        "gender_female": int(clean["gender"] == "Female"),
        "age": np.nan if clean.get("age") is None else float(clean["age"]),
        "year": float(clean["year"]),
        "cgpa_ord": float(CGPA_ORDER.index(clean["cgpa"])),
        "married": int(clean["married"]),
        "course_group": clean["course_group"],
        "anxiety": int(clean["anxiety"]),
        "panic": int(clean["panic"]),
        "treatment": 0,
    }
    return pd.DataFrame([row])[features]


def band(p: float) -> str:
    return "lower" if p < 0.35 else ("intermediate" if p < 0.6 else "higher")


def predict(clean: dict, artifact: dict | None = None) -> dict:
    art = artifact or load_artifact()
    X = to_frame(clean, art["features"])
    p = float(art["pipeline"].predict_proba(X)[0, 1])
    b = band(p)
    return {"probability": round(p, 3), "band": b, "model_version": art["version"],
            "label": ("Responses are more similar to students who self-reported depression"
                      if p >= 0.5 else
                      "Responses are less similar to students who self-reported depression")}
