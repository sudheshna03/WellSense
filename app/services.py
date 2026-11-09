"""Application service layer: the one place that wires validation -> model -> explanation -> recommendations -> DB.
Streamlit pages call these functions; they are unit-tested without Streamlit."""
from __future__ import annotations

import logging

from src.database.database import Database
from src.explainability.explainer import CAVEAT, local_explanation
from src.models.predict import predict
from src.recommendations.recommendation_engine import recommend
from src.utils.validation import validate_assessment

log = logging.getLogger("wellsense")  # never log answers


def run_assessment(db: Database, session_id: str, raw: dict, consent: bool, artifact: dict | None = None) -> dict:
    if not consent:
        return {"ok": False, "errors": ["Please tick the consent box to continue."]}
    clean, errors = validate_assessment(raw)
    if errors:
        return {"ok": False, "errors": errors}
    try:
        pred = predict(clean, artifact)
        expl = local_explanation(clean, artifact)
    except Exception:  # model missing/corrupt: fail with a clear message, no crash
        log.exception("prediction failed")
        return {"ok": False, "errors": ["The prediction model could not be loaded. Please contact the maintainer."]}
    aid = db.save_assessment(session_id, clean)
    db.save_prediction(aid, session_id, pred)
    recs = recommend(clean, pred, db.category_stats(session_id))
    recs = db.save_recommendations(aid, session_id, recs)
    return {"ok": True, "assessment_id": aid, "prediction": pred, "explanation": expl, "caveat": CAVEAT,
            "recommendations": recs}


def submit_feedback(db: Database, session_id: str, recommendation_id: int, value: str, note: str = "") -> None:
    db.save_feedback(recommendation_id, session_id, value, note)


def refresh_ranking(db: Database, session_id: str, raw: dict, artifact: dict | None = None) -> list[dict]:
    """Re-rank the same student's recommendations using their feedback so far (no new assessment saved)."""
    clean, errors = validate_assessment(raw)
    if errors:
        return []
    return recommend(clean, predict(clean, artifact), db.category_stats(session_id))
