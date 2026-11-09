import streamlit as st

from app.state import disclaimer, header, safe_page_link

header("Prediction Results")
res = st.session_state.get("result")
if not res:
    st.warning("No assessment yet.")
    safe_page_link("pages/2_Assessment.py", label="Take the assessment →")
    st.stop()

p = res["prediction"]
st.subheader(p["label"])
st.metric("Model estimate (uncalibrated score)", f"{p['probability']:.0%}", help="Band: " + p["band"])
st.caption("The target is a student's *self-reported* depression answer in a 101-student survey. This score is not "
           "a calibrated probability and is not a diagnosis.")

st.subheader("What the model responded to")
if res["explanation"]:
    for e in res["explanation"]:
        st.write("↑" if e["direction"] == "raises" else "↓", e["text"])
else:
    st.write("No single answer moved the estimate noticeably.")
st.caption(res["caveat"])
st.warning("Known limitation: in this small dataset every married student reported depression, so the model leans "
           "heavily on marital status. Treat that as a data artefact, not a real-world rule.")
disclaimer()
safe_page_link("pages/4_Personalized_Recommendations.py", label="See personalised suggestions →")
