"""WellSense entry point. Run:  streamlit run app/main.py   (requires streamlit>=1.36)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `src` and `app` importable

import streamlit as st

st.set_page_config(page_title="WellSense", page_icon="🌿", layout="centered")
pages = [
    st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/2_Assessment.py", title="Assessment", icon="📝"),
    st.Page("pages/3_Prediction_Results.py", title="Prediction Results", icon="📊"),
    st.Page("pages/4_Personalized_Recommendations.py", title="Recommendations", icon="💡"),
    st.Page("pages/5_Feedback_and_History.py", title="Feedback & History", icon="🗂️"),
    st.Page("pages/6_About_and_Privacy.py", title="About & Privacy", icon="🔒"),
]
st.navigation(pages).run()
