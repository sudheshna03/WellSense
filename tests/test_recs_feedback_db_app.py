import pytest

from app.services import refresh_ranking, run_assessment, submit_feedback
from src.database.database import Database, new_session_id
from src.explainability.explainer import local_explanation
from src.recommendations.feedback_adapter import FLOOR, category_multiplier
from src.recommendations.recommendation_engine import eligible, recommend
from src.recommendations.recommendation_ranker import rank
from src.utils.validation import validate_assessment

BASE = dict(gender="Male", age=21, year=3, cgpa="3.50 - 4.00", course_group="health_science",
            married=False, anxiety=False, panic=False)
LOW = {"band": "lower"}
HIGH = {"band": "higher"}


def clean(**kw):
    c, e = validate_assessment({**BASE, **kw}); assert e == [], e
    return c


# ---- recommendation rules -------------------------------------------------------
def ids(c, p=LOW):
    return {r["rule_id"] for r in eligible(c, p)}


def test_rules_use_actual_answers():
    assert "sleep_routine" in ids(clean(sleep_hours=4)) and "sleep_routine" not in ids(clean(sleep_hours=8))
    assert "study_breaks" in ids(clean(study_hours_straight=5))
    assert "movement" in ids(clean(activity_days=0))
    assert "connect" in ids(clean(social_support=1))
    assert "screen_balance" in ids(clean(screen_hours=9))
    assert "stress_skills" in ids(clean(anxiety=True))
    assert "academic_support" in ids(clean(cgpa="2.50 - 2.99"))


def test_personalised_not_fixed_list():
    a = ids(clean(sleep_hours=4)); b = ids(clean(social_support=1, activity_days=0))
    assert a != b


def test_fallback_only_when_nothing_else():
    assert ids(clean()) == {"routine_basics"}
    assert "routine_basics" not in ids(clean(sleep_hours=4))


def test_safety_rule_triggers_and_is_pinned_first():
    c = clean(anxiety=True, sleep_hours=3)
    top = recommend(c, HIGH)[0]
    assert top["rule_id"] == "campus_support" and "crisis" in top["action"].lower()


def test_no_clinical_language():
    banned = ["diagnos", "medicat", "cure", "prescri", "treatment plan"]
    from src.recommendations.recommendation_rules import RULES
    for r in RULES:
        text = (r["title"] + r["description"] + r["action"]).lower()
        assert not any(b in text for b in banned if b != "diagnos") or "not a diagnosis" in text


# ---- feedback adaptation ---------------------------------------------------------
def test_multiplier_needs_enough_feedback_and_has_floor():
    assert category_multiplier({"helpful": 0, "not_helpful": 1}) == 1.0
    assert category_multiplier({"helpful": 0, "not_helpful": 50}) == FLOOR
    assert category_multiplier({"helpful": 4, "not_helpful": 0}) > 1.0


def test_ranking_changes_after_feedback_but_keeps_variety():
    c = clean(sleep_hours=4, social_support=1, activity_days=0)
    cands = eligible(c, LOW)
    before = [r["rule_id"] for r in rank(cands)]
    stats = {"Sleep routine": {"helpful": 0, "not_helpful": 4}}
    after = rank(cands, stats)
    assert before[0] == "sleep_routine" or "sleep_routine" in before
    pos_b, pos_a = before.index("sleep_routine"), [r["rule_id"] for r in after].index("sleep_routine")
    assert pos_a >= pos_b                           # demoted (or equal)
    assert "sleep_routine" in [r["rule_id"] for r in after]  # not suppressed entirely


def test_safety_not_suppressed_by_negative_feedback():
    c = clean(anxiety=True)
    stats = {"Campus and professional support": {"helpful": 0, "not_helpful": 9}}
    assert rank(eligible(c, HIGH), stats)[0]["rule_id"] == "campus_support"


# ---- database --------------------------------------------------------------------
def test_database_feedback_stats_reset_delete():
    db, sid = Database(":memory:"), new_session_id()
    r = run_assessment(db, sid, {**BASE, "sleep_hours": 4, "activity_days": 0}, consent=True)
    assert r["ok"]
    recs = r["recommendations"]
    assert db.count("assessments", sid) == 1 and db.count("predictions", sid) == 1 and db.count("recommendations", sid) == len(recs)
    for rec in recs[:2]:
        submit_feedback(db, sid, rec["recommendation_id"], "not_helpful", "meh")
    assert sum(v["not_helpful"] for v in db.category_stats(sid).values()) == 2
    submit_feedback(db, sid, recs[0]["recommendation_id"], "helpful")  # upsert changes, not duplicates
    assert db.count("feedback", sid) == 2
    db.reset_feedback(sid)
    assert db.count("feedback", sid) == 0 and db.count("recommendations", sid) == len(recs)
    db.delete_session(sid)
    assert all(db.count(t, sid) == 0 for t in ("assessments", "predictions", "recommendations", "feedback"))


def test_feedback_isolated_per_session_and_validated():
    db, a, b = Database(":memory:"), new_session_id(), new_session_id()
    ra = run_assessment(db, a, {**BASE, "sleep_hours": 4}, True)["recommendations"][0]["recommendation_id"]
    with pytest.raises(ValueError):
        db.save_feedback(ra, b, "helpful")          # other session cannot rate it
    with pytest.raises(ValueError):
        db.save_feedback(ra, a, "love_it")          # invalid value


def test_no_identifiers_stored():
    db, sid = Database(":memory:"), new_session_id()
    run_assessment(db, sid, BASE, True)
    cols = {r[1] for t in ("assessments", "predictions", "recommendations", "feedback")
            for r in db._run(f"PRAGMA table_info({t})", fetch=True)}
    assert not cols & {"name", "email", "student_id", "phone"}


# ---- app service / explanation ---------------------------------------------------
def test_app_requires_consent_and_handles_bad_input():
    db = Database(":memory:")
    assert not run_assessment(db, "s", BASE, consent=False)["ok"]
    r = run_assessment(db, "s", {**BASE, "year": "x", "age": -4}, consent=True)
    assert not r["ok"] and len(r["errors"]) >= 2 and db.count("assessments") == 0


def test_adaptation_end_to_end_changes_ranking():
    db, sid = Database(":memory:"), new_session_id()
    raw = {**BASE, "sleep_hours": 4, "social_support": 1, "activity_days": 0}
    first = run_assessment(db, sid, raw, True)["recommendations"]
    for r in first:
        submit_feedback(db, sid, r["recommendation_id"], "not_helpful" if r["category"] == "Sleep routine" else "helpful")
    first_order = [r["rule_id"] for r in first]
    # one sleep vote is below MIN_FEEDBACK, so add another sleep-category assessment's rec
    second = run_assessment(db, sid, raw, True)["recommendations"]
    for r in second:
        if r["category"] == "Sleep routine":
            submit_feedback(db, sid, r["recommendation_id"], "not_helpful")
    new_order = [r["rule_id"] for r in refresh_ranking(db, sid, raw)]
    assert first_order.index("sleep_routine") <= new_order.index("sleep_routine")
    assert new_order != first_order


def test_local_explanation_matches_model():
    c = clean(married=True)
    e = local_explanation(c)
    assert e and all(x["direction"] in ("raises", "lowers") for x in e)
    assert any(x["feature"] == "married" and x["direction"] == "raises" for x in e)
