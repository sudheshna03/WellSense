import streamlit as st

from app.services import run_assessment
from app.state import disclaimer, get_db, header, safe_page_link, session_id
from src.data.preprocessing import CGPA_ORDER
from src.utils.validation import COURSE_GROUPS, LIFESTYLE

header("Assessment", "About 2 minutes. Skip anything optional you prefer not to answer.")
disclaimer()

with st.form("assessment"):
    st.subheader("About your studies (used by the model)")
    gender = st.selectbox("Gender (as coded in the original survey)", ["", "Female", "Male"])
    age = st.number_input("Age (optional)", min_value=0, max_value=100, value=0, help="Leave 0 to skip")
    year = st.selectbox("Year of study", [1, 2, 3, 4])
    cgpa = st.selectbox("CGPA band", [""] + CGPA_ORDER)
    course = st.selectbox("Course group", [""] + list(COURSE_GROUPS), format_func=lambda k: COURSE_GROUPS.get(k, "Select…"))
    married = st.radio("Married?", ["No", "Yes"], horizontal=True)
    anxiety = st.radio("Do you experience anxiety?", ["No", "Yes"], horizontal=True)
    panic = st.radio("Do you experience panic attacks?", ["No", "Yes"], horizontal=True)

    st.subheader("Daily habits (optional; used only for suggestions)")
    life = {}
    for k, (label, lo, hi) in LIFESTYLE.items():
        v = st.number_input(label, min_value=float(lo) - 1, max_value=float(hi), value=float(lo) - 1,
                            help="Leave at the minimum to skip", key=k)
        if v >= lo:
            life[k] = v

    consent = st.checkbox("I understand this is an educational prototype, not a diagnosis, and I agree that my answers "
                          "are stored locally under a random id (I can delete them at any time).")
    go = st.form_submit_button("See my results")

if go:
    raw = {"gender": gender or None, "age": age if age > 0 else None, "year": year, "cgpa": cgpa or None,
           "course_group": course or None, "married": married, "anxiety": anxiety, "panic": panic, **life}
    res = run_assessment(get_db(), session_id(), raw, consent)
    if res["ok"]:
        st.session_state["result"], st.session_state["raw"] = res, raw
        st.success("Done! Open **Prediction Results** in the sidebar.")
        safe_page_link("pages/3_Prediction_Results.py", label="Go to results →")
    else:
        for e in res["errors"]:
            st.error(e)
