"""Input validation for the assessment form. Returns clean values or clear error messages."""
from __future__ import annotations

from src.data.preprocessing import CGPA_ORDER

COURSE_GROUPS = {
    "engineering_it": "Engineering / IT / Computer science",
    "health_science": "Health, life or natural sciences, psychology, maths",
    "islamic_studies": "Islamic studies / education",
    "business_law_other": "Business, law, communication, other professional",
    "other": "Other",
}

# optional lifestyle questions: key -> (label, min, max). Used ONLY by the recommendation engine.
LIFESTYLE = {
    "sleep_hours": ("Average hours of sleep per night", 0, 14),
    "study_hours_straight": ("Longest study stretch without a break (hours)", 0, 14),
    "activity_days": ("Days per week with 20+ minutes of physical activity", 0, 7),
    "screen_hours": ("Recreational screen time per day (hours)", 0, 18),
    "social_support": ("I have someone I can talk to (1 = not at all, 5 = definitely)", 1, 5),
    "planning_difficulty": ("Difficulty planning study time (1 = none, 5 = a lot)", 1, 5),
}


def _to_bool(v, name, errors):
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("yes", "no"):
        return v.strip().lower() == "yes"
    errors.append(f"'{name}' must be Yes or No.")
    return None


def validate_assessment(raw: dict) -> tuple[dict, list[str]]:
    """Validate a raw answer dict. Returns (clean, errors); clean is only usable if errors == []."""
    errors: list[str] = []
    raw = raw or {}
    clean: dict = {}

    g = raw.get("gender")
    if g not in ("Female", "Male"):
        errors.append("Please select a gender (Female or Male) - this is the dataset's coding.")
    clean["gender"] = g

    age = raw.get("age")
    if age in (None, ""):
        clean["age"] = None  # optional; imputed inside the pipeline
    else:
        try:
            a = int(age)
            if not 16 <= a <= 60:
                raise ValueError
            clean["age"] = a
        except (TypeError, ValueError):
            errors.append("Age must be a whole number between 16 and 60 (or left blank).")
            clean["age"] = None

    try:
        y = int(raw.get("year"))
        if y not in (1, 2, 3, 4):
            raise ValueError
        clean["year"] = y
    except (TypeError, ValueError):
        errors.append("Year of study must be 1, 2, 3 or 4 (the range the model was built on).")
        clean["year"] = None

    if raw.get("cgpa") not in CGPA_ORDER:
        errors.append("Please choose a CGPA band from the list.")
    clean["cgpa"] = raw.get("cgpa")

    if raw.get("course_group") not in COURSE_GROUPS:
        errors.append("Please choose a course group from the list.")
    clean["course_group"] = raw.get("course_group")

    for k, label in (("married", "Marital status (married)"), ("anxiety", "Anxiety"), ("panic", "Panic attacks")):
        clean[k] = _to_bool(raw.get(k), label, errors)

    life = {}
    for k, (label, lo, hi) in LIFESTYLE.items():
        v = raw.get(k)
        if v in (None, ""):
            continue
        try:
            f = float(v)
            if not lo <= f <= hi:
                raise ValueError
            life[k] = f
        except (TypeError, ValueError):
            errors.append(f"'{label}' must be a number between {lo} and {hi}.")
    clean["lifestyle"] = life
    return clean, errors
