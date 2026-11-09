import streamlit as st

from app.state import disclaimer, header

header("About, Research & Privacy")
st.markdown("""
**Objective.** Extend a student mental-health prediction system with a neural-network model, explanations,
personalised non-clinical suggestions and feedback-adaptive ranking.

**Base paper.** Nath et al. (2025), *Smart web interface for student mental health prediction using machine learning
with blockchain technology*, Neuroscience Informatics 5, 100236 (doi:10.1016/j.neuri.2025.100236).

**Data.** The model was trained on the public Kaggle "Student Mental Health" survey: 101 students, 35 self-reporting
depression. It does not include the paper's additional 400 records.

**Honest results.** In repeated nested cross-validation the neural network (balanced accuracy ≈ 0.74 ± 0.11) performed
about the same as classical models; it did not beat them, and these figures are not comparable with the base paper's
reported 95.6%.

**Limitations.** Tiny, self-reported, mostly female and young sample; the model relies heavily on marital status
because of a 16/16 pattern in the data; scores are not calibrated; no outcome study of the suggestions has been done.

**Privacy.** No names, emails or student IDs. Answers live in a local SQLite file under a random session id, never in a
public blockchain. Delete everything on the *Feedback & History* page.
""")
disclaimer()
