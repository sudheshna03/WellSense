# Model card - wellsense-mlp-v1
- **Model:** scikit-learn MLPClassifier, hidden (32,16), L2 alpha=1.0, max_iter=200, Adam; preprocessing (median impute + scale, one-hot course group) inside the saved pipeline.
- **Features (tier B):** gender, age, year, CGPA band, married, course group, anxiety, panic attack.
- **Target:** self-reported depression (Yes/No). Not a diagnosis.
- **Selection:** tuned by inner 3-fold CV on training folds; final fit on all 101 rows (inner 5-fold for hyper-parameters). Deployed because it ties the best classical model, matching the project's DL objective, not because it is better.
- **Evaluation:** 5x5 repeated stratified nested CV, tier B balanced accuracy 0.735 +/- 0.111 (Random Forest 0.739, majority baseline 0.500). Full tables: `results/tables/`.
- **Intended use:** educational demonstration. **Out of scope:** diagnosis, screening, or decisions about individuals.
