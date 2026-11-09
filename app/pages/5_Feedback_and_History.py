import pandas as pd
import streamlit as st

from app.state import get_db, header, session_id
from src.recommendations.feedback_adapter import MIN_FEEDBACK, multipliers

header("Feedback & History")
db, sid = get_db(), session_id()
hist = db.history(sid)
if hist:
    try:
        st.dataframe(pd.DataFrame(hist).drop(columns=["recommendation_id"]), width="stretch")
    except TypeError:
        st.dataframe(pd.DataFrame(hist).drop(columns=["recommendation_id"]), use_container_width=True)
    stats = db.category_stats(sid)
    st.subheader("How your feedback changes ranking")
    st.caption(f"A category's weight changes only after at least {MIN_FEEDBACK} helpful/not-helpful ratings, and never "
               "drops below 0.5×, so alternatives stay visible. Safety-related support is never hidden.")
    st.table(pd.DataFrame([{"category": c, **s, "ranking weight": round(multipliers(stats)[c], 2)} for c, s in stats.items()])
             if stats else pd.DataFrame({"info": ["No feedback yet"]}))
else:
    st.info("Nothing stored for this session yet.")

st.subheader("Your data")
c1, c2 = st.columns(2)
if c1.button("Reset my feedback"):
    db.reset_feedback(sid); st.success("Feedback cleared.")
if c2.button("Delete ALL my stored data", type="primary"):
    db.delete_session(sid)
    for k in ("result", "raw"):
        st.session_state.pop(k, None)
    st.success("All data for this session was deleted.")
