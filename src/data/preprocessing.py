"""Reusable preprocessing for WellSense. All fitted transforms live inside an sklearn Pipeline,
so they are fit on training folds only (no leakage)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "raw" / "student_mental_health.csv"
TARGET_RAW = "Do you have Depression?"

CGPA_ORDER = ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"]

# Feature tiers (see docs/base_paper_analysis.md and the Phase 1 report)
TIER_A = ["gender_female", "age", "year", "cgpa_ord", "married", "course_group"]
TIER_B = TIER_A + ["anxiety", "panic"]
TIER_C = TIER_B + ["treatment"]  # sensitivity analysis only: likely downstream of the label
TIERS = {"A": TIER_A, "B": TIER_B, "C": TIER_C}

_COURSE_RULES = [
    ("engineering_it", ["engin", "bcs", "bit", "it", "koe", "kop", "enm", "benl", "cts", "computer"]),
    ("islamic_studies", ["islam", "pendidikan", "fiqh", "usuluddin", "irkhs", "kirkhs", "taasl", "ala", "kenms"]),
    ("health_science", ["biomed", "nurs", "radiograph", "mhsc", "biotech", "marine", "human sci", "psycholog", "mathem"]),
    ("business_law_other", ["law", "account", "bank", "business", "econ", "human res", "communic", "tesl"]),
]


def course_group(text: str) -> str:
    t = str(text).strip().lower()
    for group, keys in _COURSE_RULES:
        if any(t == k or (len(k) > 3 and k in t) for k in keys):
            return group
    return "other"


def load_clean(path: Path = CSV) -> tuple[pd.DataFrame, pd.Series]:
    """Load the raw CSV, normalise labels, drop Timestamp, return (features, target)."""
    raw = pd.read_csv(path)
    yes = lambda s: (s.astype(str).str.strip().str.lower() == "yes").astype(int)
    X = pd.DataFrame({
        "gender_female": (raw["Choose your gender"].str.strip().str.lower() == "female").astype(int),
        "age": raw["Age"],  # NaN kept; imputed inside the pipeline (train folds only)
        "year": raw["Your current year of Study"].str.lower().str.extract(r"(\d)")[0].astype(float),
        "cgpa_ord": raw["What is your CGPA?"].str.strip().map({c: i for i, c in enumerate(CGPA_ORDER)}),
        "married": yes(raw["Marital status"]),
        "course_group": raw["What is your course?"].map(course_group),
        "anxiety": yes(raw["Do you have Anxiety?"]),
        "panic": yes(raw["Do you have Panic attack?"]),
        "treatment": yes(raw["Did you seek any specialist for a treatment?"]),
    })
    y = yes(raw[TARGET_RAW]).rename("depression_self_report")
    return X, y


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    numeric = [f for f in ("age", "year", "cgpa_ord") if f in features]
    categorical = [f for f in ("course_group",) if f in features]
    binary = [f for f in features if f not in numeric + categorical]
    transformers = [
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), numeric),
        ("bin", "passthrough", binary),
    ]
    if categorical:
        transformers.append(("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical))
    return ColumnTransformer(transformers)
