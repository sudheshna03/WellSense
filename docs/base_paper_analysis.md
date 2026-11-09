# Base Paper Analysis

**Paper:** Nath, M.D., Ahamed, M.K.U., Ahmed, O., Ahmed, T., Roy, S., Uddin, M.N. (2025). *Smart web interface for student mental health prediction using machine learning with blockchain technology.* Neuroscience Informatics 5, 100236. DOI: 10.1016/j.neuri.2025.100236.

All statements below come from the PDF supplied by the project owner. Items marked **[observation]** are my own checks of the paper's figures and are not claims made by the authors.

## 1. Summary
The authors predict whether a student reports depression from a few demographic, academic and self-reported mental-health fields. They compare 12 ML classifiers, pick the top six, build a Random Forest-based model reported at 95.6% accuracy, deploy it in a Streamlit app, and store submitted form data on an Ethereum (Ganache/MetaMask/Solidity/Truffle) blockchain.

## 2. Original methodology
- **Task:** binary classification; label 1 = student reports depression, 0 = no depression (Sec. 3.4.1).
- **Descriptive stats / EDA:** mean, median, SD, box plots, Pearson heatmap, ANOVA (CGPA vs year/gender), chi-square plots.
- **Missing values:** median (numerical), mode (categorical).
- **Outliers:** IQR rule (1.5×IQR), values capped.
- **Encoding:** label encoding (ordinal/binary), one-hot (nominal).
- **Scaling:** StandardScaler.
- **Feature selection:** correlation + significance tests, then Recursive Feature Elimination (Algorithm 2).
- **Models:** 12 classifiers incl. Logistic Regression, Decision Tree, Extra Trees, AdaBoost, Gradient Boosting, XGBoost, Voting, SVC, KNN, Naive Bayes, Linear Regression, Random Forest. Top six reported: LR, DT, ET, AdaBoost, GB, XGBoost.
- **Tuning:** grid search and random search.
- **Split:** stated as 70% train / 30% test (Sec. 3.9).
- **Metrics:** accuracy, precision, recall, F1, MCC, confusion matrix, ROC/AUC, 5-fold accuracy (Table 6).

## 3. Original architecture
Dataset → preprocessing → model training/selection → Streamlit UI (sliders of encoded values) → prediction + probability → form entry stored via Web3 to an Ethereum smart contract (Ganache local chain, MetaMask signing).

## 4. Original dataset
| Source | Size (as stated) |
|---|---|
| Kaggle "Student Mental Health" (shariful07) | 100 students |
| Mendeley "Student mental health related records" (hy4653fg79) | 400 students, Bangladeshi universities |

Stated total: 500 records (later 501), 10 features: gender, age, course, year of study, CGPA, marital status, anxiety, panic attack, seeking treatment, plus target Depression. Class counts: 315 (no depression) / 185–186 (depression).

## 5. Original reported results
- Random Forest: **95.6% accuracy** (reported by the authors; fold-wise RF mean ≈ 95.32%, Table 6).
- Top individual models: DT 93.42%, ET 92.21%, AdaBoost 94.2%, GB 93.42%, XGBoost 95% (Sec. 3.9); other sections/figures show different values for the same models (e.g. Fig. 16 reports XGBoost 90.0%, GB 88.0%), so figures are not mutually consistent.
- Fig. 8: Anxiety is the most important feature, followed by year of study, age, marital status, panic attack.

## 6. Limitations
**Acknowledged by the authors (Sec. 5):** small and non-diverse data; self-reported labels (bias risk); feature set not exhaustive (social, economic, environmental factors missing); black-box models limit interpretability; privacy, latency and integration concerns; no longitudinal data; needs validation across institutions.
**Additional issues I noticed [observation]:**
- Stated sizes are inconsistent: 500 vs 501 records; 185 vs 186 positives; the Kaggle part is stated as 100 students while the supplied CSV has 101 rows (100 with age).
- A 70/30 split of ~501 rows would give ~150 test cases, but the confusion matrices in Figs. 13–14 sum to 101 test cases.
- The RF confusion matrix in Fig. 14 (64, 4, 1, 32) corresponds to 96/101 = 95.0%, not 95.6%.
- Predictors include other self-reported conditions (anxiety, panic attack) and treatment-seeking, which may be outcomes of the same condition rather than independent predictors. The correlation heatmap (Fig. 7) also includes `Timestamp` as a feature.
- The text calls the final model a Random Forest but also describes it as combining DT/AdaBoost/GB/ET/XGBoost/KNN; the exact architecture is unclear.
- The abstract/discussion mention explainability, but the only interpretation I found is a feature-importance bar chart (Fig. 8); no SHAP/LIME-style per-prediction explanation is described.
- Ethics approval and consent are marked "Not applicable" although the app stores sensitive health data.
- The Mendeley records are not part of the CSV supplied here, so the paper's experiment cannot be reproduced exactly.

## 7. Future work stated by the authors
More comprehensive and diverse datasets, improved interpretability, stronger privacy-preserving mechanisms, longitudinal data, multi-institution validation.

## 8. Proposed WellSense improvements (plan, not yet implemented)
1. Fair, leakage-aware comparison of ML baselines and a compact ANN/MLP under identical repeated stratified CV.
2. Preprocessing fitted inside CV folds only; ordinal CGPA/year; grouped course.
3. Explainability (SHAP/coefficients) globally and per prediction.
4. Rule-based, non-clinical recommendations, ranked by per-student feedback.
5. Privacy-first local SQLite storage with deletion, instead of a public blockchain.
6. Honest reporting, including when the ANN does not win.

## 9. Comparison table
| Aspect | Base paper (as reported) | WellSense (planned) |
|---|---|---|
| Target | Self-reported depression | Same, labelled as self-report, not diagnosis |
| Models | 12 classical ML, RF best | Dummy, LR, DT, RF, SVM, boosting + ANN/MLP |
| Deep learning | None in own experiments | Compact ANN/MLP as core component |
| Validation | Single split + 5-fold | Repeated stratified CV; test set untouched for tuning |
| Leakage handling | Not discussed | Explicit feature-tier analysis |
| Explainability | Feature-importance chart | Global + per-prediction explanations |
| Output | Prediction + probability | Prediction + explanation + recommendations |
| Personalisation / feedback | None | Feedback-adaptive ranking |
| Storage | Public-style Ethereum chain | Local database, pseudonymous IDs, deletion |
| Reported accuracy | 95.6% (authors' result) | To be measured; no claim yet |
