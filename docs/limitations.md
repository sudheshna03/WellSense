# Limitations
- **Data:** 101 students, 35 positives; mostly female and aged 18-24; self-reported labels; single-source survey. The base paper's extra 400 Mendeley records were not available.
- **Marital-status artefact:** all 16 married students report depression. Out-of-fold permutation importance is dominated by marital status (0.188 drop in balanced accuracy vs 0.037 for anxiety). The model's behaviour largely reflects this small-sample pattern, so its predictions should not be over-trusted.
- **Circularity:** anxiety and panic attack are co-reported conditions; treatment-seeking is likely downstream of the label (tier C is a sensitivity analysis only; the app never asks for it).
- **DL vs ML:** the tuned MLP did not outperform classical models (differences within fold noise). No improvement is claimed.
- **Not comparable with the base paper's 95.6%:** different data, split and evaluation protocol; the paper's own figures are internally inconsistent (see `base_paper_analysis.md`).
- **Scores are not calibrated**; the app shows an "uncalibrated score" and bands.
- **Recommendations** are rule-based and untested for effect on wellbeing. Ranking adaptation is verified by unit tests and a scripted demo, not by a user study.
- **Tooling:** no TensorFlow/SHAP/Streamlit runtime in the build environment (see README).
