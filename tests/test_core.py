import numpy as np
import pandas as pd
import pytest
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from src.data.preprocessing import TIER_A, TIER_B, TIER_C, build_preprocessor, course_group, load_clean
from src.models.predict import load_artifact, predict, to_frame
from src.utils.validation import validate_assessment

GOOD = dict(gender="Female", age=20, year=2, cgpa="3.00 - 3.49", course_group="engineering_it",
            married=False, anxiety=True, panic=False)


# ---- data loading / preprocessing -------------------------------------------------
def test_data_loading_shapes_and_target():
    X, y = load_clean()
    assert X.shape[0] == 101 == len(y)
    assert set(y.unique()) == {0, 1} and int(y.sum()) == 35
    assert "Timestamp" not in X.columns


def test_label_cleaning():
    X, _ = load_clean()
    assert set(X.year.dropna().unique()) == {1.0, 2.0, 3.0, 4.0}
    assert X.cgpa_ord.notna().all() and X.cgpa_ord.between(0, 4).all()
    assert course_group("Engine") == "engineering_it" and course_group("Pendidikan Islam") == "islamic_studies"


def test_missing_age_imputed_from_train_only():
    X, y = load_clean()
    prep = build_preprocessor(TIER_A)
    tr = X.iloc[:50]
    prep.fit(tr)
    te = X.iloc[50:].copy(); te["age"] = np.nan
    out = prep.transform(te)
    assert not np.isnan(out).any()
    med = tr["age"].median()
    assert prep.named_transformers_["num"].named_steps["imp"].statistics_[0] == med  # test data never used


def test_feature_tiers_exclude_leaky_columns_from_primary():
    assert "treatment" not in TIER_A and "treatment" not in TIER_B and "treatment" in TIER_C
    assert "anxiety" not in TIER_A


def test_feature_order_consistent_at_inference():
    art = load_artifact()
    X = to_frame(validate_assessment(GOOD)[0], art["features"])
    assert list(X.columns) == art["features"]


# ---- ANN --------------------------------------------------------------------------
def test_ann_output_shape_and_probabilities():
    X, y = load_clean()
    pipe = Pipeline([("prep", build_preprocessor(TIER_B)),
                     ("clf", MLPClassifier((32, 16), alpha=0.1, max_iter=200, random_state=42))]).fit(X[TIER_B], y)
    p = pipe.predict_proba(X[TIER_B].iloc[:5])
    assert p.shape == (5, 2) and np.allclose(p.sum(axis=1), 1)
    assert [l.shape for l in pipe.named_steps["clf"].coefs_] == [(pipe.named_steps["prep"].transform(X[TIER_B]).shape[1], 32), (32, 16), (16, 1)]


# ---- prediction / validation ------------------------------------------------------
def test_prediction_format():
    r = predict(validate_assessment(GOOD)[0])
    assert 0 <= r["probability"] <= 1 and r["band"] in ("lower", "intermediate", "higher") and r["model_version"]


@pytest.mark.parametrize("bad,frag", [
    ({**GOOD, "gender": None}, "gender"), ({**GOOD, "age": "abc"}, "Age"), ({**GOOD, "age": 5}, "Age"),
    ({**GOOD, "year": 9}, "Year"), ({**GOOD, "cgpa": "5.0"}, "CGPA"), ({**GOOD, "anxiety": None}, "Anxiety"),
    ({**GOOD, "sleep_hours": 40}, "sleep"), ({}, "gender"),
])
def test_invalid_input_gives_clear_errors(bad, frag):
    _, errs = validate_assessment(bad)
    assert errs and any(frag.lower() in e.lower() for e in errs)


def test_blank_age_allowed_and_predicts():
    clean, errs = validate_assessment({**GOOD, "age": ""})
    assert errs == [] and 0 <= predict(clean)["probability"] <= 1
