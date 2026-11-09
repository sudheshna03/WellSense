# WellSense
Explainable student wellbeing-support prototype extending Nath et al. (2025), *Smart web interface for student mental health prediction using machine learning with blockchain technology* (doi:10.1016/j.neuri.2025.100236).
**Not a medical or clinical diagnostic system.** Target = a student's *self-reported* depression answer.

## Setup (Windows PowerShell)
```
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```
Put the Kaggle "Student Mental health.csv" at `data/raw/student_mental_health.csv`.

## Reproduce
```
python -m src.data.inspect_dataset          # dataset report + figures
python -m src.models.run_experiments        # nested repeated-CV comparison (~15-20 min)
python -m src.models.train_final            # saves models/dl/wellsense_mlp_v1.joblib
python -m src.explainability.global_explanation
python -m src.evaluation.ablation_study
python -m src.evaluation.generate_figures
python -m pytest                            # 30 tests
python scripts/smoke_test_app.py            # headless Streamlit AppTest smoke suite
streamlit run app/main.py                   # interactive app
```
Seed 42 everywhere. Results are written to `results/`.

## Honest status
- DL model = scikit-learn `MLPClassifier` (32-16, L2, Adam), **not Keras**: TensorFlow could not be installed in the build environment. A Keras port is possible on your machine but has not been run.
- Explanations use occlusion and permutation importance, **not SHAP** (same reason).
- Streamlit pages have been headlessly verified with Streamlit `AppTest` (`scripts/smoke_test_app.py`) covering all pages, interactive full flows, and input error handling, as well as live HTTP serving.
- No real recommendation-feedback data exists, so no feedback-effectiveness claim is made.
See `docs/limitations.md` and `docs/model_card.md`.
