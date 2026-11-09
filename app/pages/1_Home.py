import streamlit as st

from app.state import disclaimer, header, safe_page_link

header("🌿 WellSense", "Explainable student wellbeing-support prototype")
st.write("WellSense compares your answers with a small survey of students, explains which answers the model "
         "responded to, and suggests practical, non-clinical habits. You can rate each suggestion, and future "
         "suggestions are re-ranked using *your* ratings.")
st.markdown("**How it works:** 1) answer a short questionnaire → 2) see the model's estimate and an explanation → "
            "3) get personalised suggestions → 4) tell us which helped.")
safe_page_link("pages/2_Assessment.py", label="Start the assessment →", icon="📝")
st.subheader("Privacy in brief")
st.write("No name, email or student ID is collected. Answers are stored locally under a random session id and "
         "you can delete everything on the *Feedback & History* page.")
disclaimer()
