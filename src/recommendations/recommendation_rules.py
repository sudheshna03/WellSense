"""Transparent, non-clinical recommendation rules. Each rule only uses answers that actually exist.

fn(clean, prediction) -> (need_strength 0..1, reason) or None when the rule does not apply.
"""
from __future__ import annotations

DISCLAIMER = ("WellSense is an educational wellbeing-support prototype. It is not a medical or clinical diagnostic "
              "system and is not a substitute for professional support.")
CRISIS_NOTE = ("If you feel unsafe or in crisis, contact your local emergency number or a crisis line right away, "
               "or reach out to someone you trust.")


def _life(c, k):
    return c.get("lifestyle", {}).get(k)


def r_sleep(c, p):
    s = _life(c, "sleep_hours")
    if s is not None and s < 7:
        return min(1.0, 0.4 + (7 - s) / 3), f"You reported about {s:g} hours of sleep per night."


def r_planning(c, p):
    d = _life(c, "planning_difficulty")
    if d is not None and d >= 3:
        return 0.3 + 0.14 * d, f"You rated difficulty planning study time as {d:g}/5."


def r_breaks(c, p):
    h = _life(c, "study_hours_straight")
    if h is not None and h >= 3:
        return min(1.0, 0.3 + 0.12 * h), f"Your longest study stretch without a break is about {h:g} hours."


def r_activity(c, p):
    d = _life(c, "activity_days")
    if d is not None and d <= 2:
        return 0.5 + 0.15 * (2 - d), f"You reported physical activity on {d:g} day(s) per week."


def r_screen(c, p):
    h = _life(c, "screen_hours")
    if h is not None and h >= 6:
        return min(1.0, 0.3 + 0.07 * h), f"You reported about {h:g} hours of recreational screen time per day."


def r_social(c, p):
    s = _life(c, "social_support")
    if s is not None and s <= 2:
        return 0.9 - 0.1 * s, f"You rated having someone to talk to as {s:g}/5."


def r_stress(c, p):
    if c.get("anxiety") or c.get("panic"):
        which = " and ".join(n for n, k in (("anxiety", "anxiety"), ("panic attacks", "panic")) if c.get(k))
        return 0.7, f"You reported experiencing {which}."


def r_academic(c, p):
    from src.data.preprocessing import CGPA_ORDER
    if CGPA_ORDER.index(c["cgpa"]) <= 2:
        return 0.55, f"Your reported CGPA band is {c['cgpa']}."


def r_support(c, p):
    reasons = []
    if p["band"] == "higher":
        reasons.append("the model's estimate for your answers is in the higher band")
    if c.get("anxiety") or c.get("panic"):
        reasons.append("you reported anxiety or panic attacks")
    if reasons:
        return 1.0, "Because " + " and ".join(reasons) + " (this is not a diagnosis)."


def r_general(c, p):
    return 0.1, "A small, steady routine is a good foundation whatever your answers were."


RULES = [
    dict(id="sleep_routine", category="Sleep routine", title="Build a steady sleep routine",
         description="Regular sleep and wake times can make days feel more manageable.",
         action="Pick a target bedtime and wake time you can keep for a week; stop screens 30 minutes before bed.",
         minutes=10, difficulty="easy", fn=r_sleep),
    dict(id="study_plan", category="Study planning", title="Plan your week in 15 minutes",
         description="A simple plan reduces last-minute pressure.",
         action="List the next 7 days' deadlines, choose the top 3 tasks per day, and block time for them.",
         minutes=15, difficulty="easy", fn=r_planning),
    dict(id="study_breaks", category="Concentration and breaks", title="Use short, structured breaks",
         description="Regular breaks help concentration over long study sessions.",
         action="Try 45 minutes of focused study, then a 10-minute break away from your desk.",
         minutes=10, difficulty="easy", fn=r_breaks),
    dict(id="movement", category="Physical activity", title="Add a manageable movement goal",
         description="Light regular activity is linked with better mood and energy for many people.",
         action="Start with a 15-minute walk on three days this week.",
         minutes=15, difficulty="easy", fn=r_activity),
    dict(id="screen_balance", category="Healthy screen-time habits", title="Create screen-free windows",
         description="Planned breaks from screens can protect sleep and focus.",
         action="Choose one daily 1-hour window (e.g. meals or before bed) with no recreational screens.",
         minutes=5, difficulty="medium", fn=r_screen),
    dict(id="connect", category="Social connection", title="Reach out to someone you trust",
         description="Talking with another person can lighten a heavy week.",
         action="Message a friend, family member or mentor and arrange a short chat or walk this week.",
         minutes=15, difficulty="medium", fn=r_social),
    dict(id="stress_skills", category="Stress management", title="Practise a short calming routine",
         description="Brief breathing or grounding exercises are common everyday stress-management tools.",
         action="Try 5 minutes of slow breathing (in for 4, out for 6) once a day, e.g. before study.",
         minutes=5, difficulty="easy", fn=r_stress),
    dict(id="academic_support", category="Study planning", title="Use campus academic support",
         description="Tutoring or advising can make coursework feel more manageable.",
         action="Book a short meeting with your academic advisor or a tutoring service this month.",
         minutes=30, difficulty="medium", fn=r_academic),
    dict(id="campus_support", category="Campus and professional support", title="Consider talking to a counsellor",
         description="Campus counselling services are there for students, whatever the reason.",
         action="Look up your university's counselling or student-wellbeing service and note how to book an appointment. "
                + CRISIS_NOTE,
         minutes=15, difficulty="medium", safety=True, fn=r_support),
    dict(id="routine_basics", category="Study planning", title="Keep one small daily routine",
         description="A tiny, repeatable habit is easier to maintain than a big plan.",
         action="Choose one 10-minute habit (tidy desk, short walk or planning) and do it daily for a week.",
         minutes=10, difficulty="easy", fn=r_general),
]
