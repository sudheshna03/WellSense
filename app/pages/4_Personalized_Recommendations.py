import streamlit as st

from app.services import refresh_ranking, submit_feedback
from app.state import disclaimer, get_db, header, safe_page_link, session_id

header("Personalised suggestions", "Small, practical, non-clinical steps chosen from your answers")
res = st.session_state.get("result")
if not res:
    st.warning("Complete the assessment first.")
    safe_page_link("pages/2_Assessment.py", label="Take the assessment →")
    st.stop()

db, sid = get_db(), session_id()
recs = res["recommendations"]
LABEL = {"helpful": "👍 Helpful", "not_helpful": "👎 Not helpful", "not_tried": "⏳ Not tried yet"}
for r in recs:
    with st.container(border=True):
        st.markdown(f"**{r['title']}**  ·  _{r['category']}_  ·  ~{r['minutes']} min · {r['difficulty']}")
        st.write(r["description"])
        st.caption("Why: " + r["reason"])
        st.write("**Try this:** " + r["action"])
        choice = st.radio("Was this useful?", list(LABEL), format_func=LABEL.get, index=None,
                          horizontal=True, key=f"fb{r['recommendation_id']}")
        note = st.text_input("Optional short comment", key=f"note{r['recommendation_id']}", max_chars=300)
        if st.button("Save feedback", key=f"save{r['recommendation_id']}") and choice:
            submit_feedback(db, sid, r["recommendation_id"], choice, note)
            st.success("Saved.")

if st.button("Re-rank using my feedback"):
    new = refresh_ranking(db, sid, st.session_state["raw"])
    st.write("**New order:** " + " → ".join(f"{i + 1}. {x['title']}" for i, x in enumerate(new)))
disclaimer()
