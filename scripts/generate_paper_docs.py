"""Script to generate publication-grade IEEE-styled Word (.docx) and PDF (.pdf) documents
for the WellSense research paper.
Embeds real empirical metrics, tables, and figures from results/.
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DOCX_PATH = OUT_DIR / "WellSense_Research_Paper.docx"
PDF_PATH = OUT_DIR / "WellSense_Research_Paper.pdf"
HTML_PATH = OUT_DIR / "WellSense_Research_Paper.html"

# Figures
FIG_MODEL_COMP = ROOT / "results" / "figures" / "model_comparison.png"
FIG_FEAT_IMP = ROOT / "results" / "figures" / "feature_importance.png"
FIG_CONF_MAT = ROOT / "results" / "figures" / "confusion_matrix.png"
FIG_TRAIN_CURVE = ROOT / "results" / "figures" / "ann_training_curve.png"
FIG_TARGET_DIST = ROOT / "results" / "figures" / "target_distribution.png"


# ==============================================================================
# 1. WORD DOCUMENT GENERATION (.DOCX)
# ==============================================================================
def create_docx():
    print("--> Generating IEEE-styled Word Document (.docx)...")
    doc = docx.Document()

    # Section 1: Page Setup (Title, Authors, Abstract)
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(0.75)
    sec1.left_margin = Inches(0.65)
    sec1.right_margin = Inches(0.65)

    # Base font
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run(
        "WellSense: An Explainable, Privacy-Preserving, and Feedback-Adaptive Framework for Student Wellbeing Support"
    )
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(18)
    r_title.font.bold = True

    # Subtitle / Note
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run(
        "A Methodological Audit and Human-Centered System Extension of Machine Learning Baselines"
    )
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(70, 70, 70)

    # Author
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(16)
    r_auth = p_auth.add_run("Sudheshna Devi\n")
    r_auth.font.name = "Times New Roman"
    r_auth.font.size = Pt(11)
    r_auth.font.bold = True
    r_affil = p_auth.add_run(
        "Department of Computer Science and Engineering\nPrasad V. Potluri Siddhartha Institute of Technology, Vijayawada, India\nsudheshnat29@gmail.com"
    )
    r_affil.font.name = "Times New Roman"
    r_affil.font.size = Pt(9.5)
    r_affil.font.italic = True

    # Abstract Box
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.left_indent = Inches(0.2)
    p_abs.paragraph_format.right_indent = Inches(0.2)
    p_abs.paragraph_format.space_after = Pt(6)
    p_abs.paragraph_format.line_spacing = 1.05

    r_absh = p_abs.add_run("Abstract—")
    r_absh.font.name = "Times New Roman"
    r_absh.font.size = Pt(9.0)
    r_absh.font.bold = True
    r_absh.font.italic = True

    r_abst = p_abs.add_run(
        "Student mental health systems increasingly rely on predictive machine learning to detect psychological distress. "
        "However, existing systems—exemplified by the foundational study of Nath et al. (Neuroscience Informatics, 2025)—suffer from "
        "acute architectural limitations: they terminate at black-box probability scores without actionable guidance, report inflated "
        "single-split accuracies (95.6%) that do not hold under rigorous leak-free cross-validation, and propose permanently storing "
        "sensitive student mental health responses on public immutable blockchains. To address these critical gaps, this paper introduces "
        "WellSense: an explainable, privacy-preserving, and feedback-adaptive decision-support prototype. WellSense benchmarks a tuned Multi-Layer "
        "Perceptron (MLP) against seven classical classifiers under a 5x5 repeated nested cross-validation protocol (25 outer folds) across three "
        "isolated feature tiers. Empirical evaluation shows that under leak-free nested CV, the tuned MLP achieves a balanced accuracy of 0.735 ± 0.111 "
        "(accuracy: 0.782 ± 0.085, ROC AUC: 0.802 ± 0.109), proving to be statistically tied with Random Forest (0.739 ± 0.100, paired difference: -0.004). "
        "To eliminate black-box opacity, WellSense incorporates global permutation importance on held-out folds and local occlusion feature attribution, "
        "uncovering a severe dataset artifact where marital status disproportionately dominates predictions (importance: 0.1877 ± 0.0928) due to a 16/16 "
        "correlation in the survey sample. Bridging the gap between prediction and support, WellSense introduces a transparent, non-clinical recommendation "
        "engine coupled with a Bayesian-smoothed feedback loop that dynamically re-ranks lifestyle suggestions while strictly pinning safety resources. "
        "Finally, the system rejects public blockchain storage in favor of a privacy-first, local SQLite architecture with pseudonymous UUID sessions and "
        "on-demand data deletion. Framed strictly as an educational support aid rather than a clinical diagnostic instrument, WellSense provides a reproducible, "
        "methodologically honest paradigm for student wellbeing informatics."
    )
    r_abst.font.name = "Times New Roman"
    r_abst.font.size = Pt(9.0)
    r_abst.font.bold = True

    # Keywords
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.left_indent = Inches(0.2)
    p_kw.paragraph_format.right_indent = Inches(0.2)
    p_kw.paragraph_format.space_after = Pt(14)

    r_kwh = p_kw.add_run("Keywords—")
    r_kwh.font.name = "Times New Roman"
    r_kwh.font.size = Pt(9.0)
    r_kwh.font.bold = True
    r_kwh.font.italic = True

    r_kwt = p_kw.add_run(
        "Student Mental Health, Machine Learning, Multi-Layer Perceptron, Explainable AI (XAI), Feature Occlusion, "
        "Feedback Adaptation, Decision Support, Health Informatics, Privacy-by-Design, Research Integrity."
    )
    r_kwt.font.name = "Times New Roman"
    r_kwt.font.size = Pt(9.0)

    # Section 2: Two-column layout for the body
    sec2 = doc.add_section(WD_SECTION.CONTINUOUS)
    sec2.top_margin = Inches(0.75)
    sec2.bottom_margin = Inches(0.75)
    sec2.left_margin = Inches(0.65)
    sec2.right_margin = Inches(0.65)

    # Helper function for headings
    def add_sec_heading(title, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10 if level == 1 else 6)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5 if level == 1 else 9.5)
        r.font.bold = True
        if level > 1:
            r.font.italic = True
        return p

    def add_para(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        return p

    def add_fig(img_path, caption):
        if img_path.exists():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            doc.add_picture(str(img_path), width=Inches(3.3))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(6)
            r = p_cap.add_run(caption)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.0)
            r.font.italic = True

    # --- BODY CONTENT ---
    add_sec_heading("I. INTRODUCTION")
    add_para(
        "University students experience acute psychological challenges arising from rigorous academic workloads, financial pressures, "
        "and the personal transition into adulthood. While institutions frequently establish counseling centers, pervasive social stigma and "
        "resource shortages frequently delay access to timely assistance. In response, data-driven machine learning (ML) models have been proposed "
        "to screen for mental distress from self-reported student demographic and behavioral surveys."
    )
    add_para(
        "A prominent recent study by Nath et al. [1], published in Neuroscience Informatics (Elsevier, 2025), introduced a web-based prediction "
        "system combining twelve machine learning algorithms, a Streamlit interface, and an Ethereum-based blockchain storage module, reporting "
        "a headline Random Forest accuracy of 95.6%. While their work demonstrates commendable engineering ambition, our critical analysis reveals "
        "critical methodological and architectural shortcomings. First, their 95.6% result relied on a single 70/30 train/test split on a composite "
        "dataset, lacking nested cross-validation or confidence intervals. Second, their feature set included predictor variables such as treatment-seeking "
        "and acute clinical symptoms that introduce label leakage and distort real-world applicability. Third, their web application functions solely "
        "as a predictive 'black box,' leaving students with an anxiety-inducing probability score devoid of actionable support. Finally, permanently recording "
        "sensitive student mental health responses on an immutable public blockchain ledger introduces severe privacy, ethical, and regulatory risks under GDPR."
    )
    add_para(
        "To resolve these challenges, this paper presents WellSense, an end-to-end, privacy-preserving, and explainable decision-support prototype. "
        "WellSense advances student wellbeing informatics across four pillars: (1) a methodologically rigorous benchmarking of a tuned Multi-Layer Perceptron (MLP) "
        "under 5x5 repeated nested cross-validation; (2) an explicit feature-tier ablation isolating potential target leakage; (3) Explainable AI (XAI) combining "
        "global permutation importance with per-prediction occlusion explanations to expose dataset artifacts; and (4) a closed-loop recommendation engine that maps "
        "lifestyle factors to non-clinical habits, dynamically re-ranking suggestions through Bayesian-smoothed student feedback. Crucially, WellSense replaces "
        "public blockchain storage with a local, pseudonymous SQLite database with full session deletion rights."
    )

    add_sec_heading("II. RELATED WORK & BASE PAPER AUDIT")
    add_para(
        "Predictive modeling of student mental health has expanded rapidly. Baba and Bunji [2] utilized longitudinal annual health surveys across 3,561 undergraduates, "
        "demonstrating the predictive value of temporal data while emphasizing that models do not generalize across distinct institutional cohorts. Dhariwal et al. [3] "
        "and Ramasamy et al. [4] investigated multi-model ensembles for student depression detection, yet similarly terminated their workflows at point-in-time classification."
    )
    add_para(
        "The base paper by Nath et al. [1] represents the closest reference for our work. They trained 12 classifiers on 500 composite records, claiming 95.6% accuracy "
        "for a Random Forest. However, an in-depth audit reveals that their confusion matrices (e.g. 64 TN, 4 FP, 1 FN, 32 TP) sum to exactly 101 test records, "
        "matching the Kaggle 'Student Mental Health' public survey [5] rather than their stated 500-student cohort. Furthermore, feature importance in their study placed "
        "heavy reliance on treatment-seeking and anxiety—variables that co-occur contemporaneously with depression. In contrast, responsible ML guidelines, such as "
        "TRIPOD+AI [6], mandate nested validation, leakage-aware feature tiering, transparent uncertainty reporting, and strict separation between exploratory baselines and clinical claims."
    )

    add_sec_heading("III. WELLSENSE SYSTEM ARCHITECTURE")
    add_para(
        "WellSense is structured into four modular, decoupled layers: (A) Preprocessing and Leakage-Aware Tiering, (B) Neural Network and Baseline Classifiers, "
        "(C) Explainability Layer, (D) Feedback-Adaptive Recommendation Engine, and (E) Privacy-Preserving Storage."
    )

    add_sec_heading("A. Preprocessing & Feature Tiering", level=2)
    add_para(
        "To evaluate model sensitivity to feature leakage, WellSense structures the feature space into three isolated tiers: "
        "\n• Tier A (Demographic & Academic): Gender, Age, Year of Study, CGPA band, and Grouped Course Category (engineering/IT, health sciences, islamic studies, business/law, other). "
        "\n• Tier B (Primary Deployed Tier): Tier A plus self-reported psychological indicators (Anxiety, Panic Attacks, and Marital Status). To maintain ethical integrity and avoid direct target leakage, professional treatment-seeking is strictly excluded. "
        "\n• Tier C (Diagnostic Overlap Tier): All features including treatment-seeking, evaluated solely for ablation comparison."
    )
    add_para(
        "All data preprocessing—including median imputation for age, most-frequent imputation for categoricals, and one-hot encoding—is encapsulated inside "
        "scikit-learn Pipelines and fitted strictly on training folds, guaranteeing that zero out-of-fold information contaminates testing."
    )

    add_sec_heading("B. Nested Cross-Validation & Model Zoo", level=2)
    add_para(
        "WellSense benchmarks eight supervised architectures under 5x5 Repeated Stratified Cross-Validation (25 outer folds): Dummy Majority Baseline, "
        "Logistic Regression (L2 penalty), Decision Tree (depth 2–5), Random Forest (200 estimators), Support Vector Classifier (RBF kernel), "
        "Gradient Boosting (50–150 estimators), an Initial MLP (32-16 architecture, alpha=1e-4), and a Tuned MLP. The Tuned MLP undergoes inner 3-fold CV "
        "tuning across hidden layer configurations ((8,), (16,), (32, 16)), L2 regularization penalties (alpha from 0.001 to 1.0), and iteration budgets (200 to 600)."
    )

    add_sec_heading("C. Explainable AI (XAI) Framework", level=2)
    add_para(
        "To eliminate black-box opacity without introducing unstable third-party dependencies, WellSense implements a two-fold interpretability strategy: "
        "\n1) Global Permutation Importance: Evaluated across held-out test folds over 20 shuffle iterations to quantify the drop in balanced accuracy when a feature is scrambled. "
        "\n2) Local Feature Occlusion: For any given user inference, each feature is systematically substituted with its cohort median/mode. The resulting shift in predicted depression score "
        "indicates whether that specific answer elevated (↑) or reduced (↓) the model's estimate, providing clear natural-language rationale."
    )

    add_sec_heading("D. Adaptive Recommendation Engine", level=2)
    add_para(
        "Rather than burdening students with a clinical diagnosis, WellSense captures six optional lifestyle indicators: sleep hours (0–14), longest study stretch without a break (0–14), "
        "days of physical activity (0–7), recreational screen time (0–18), social support score (1–5), and study planning difficulty (1–5). A rule-based engine generates non-clinical, actionable habits."
    )
    add_para(
        "Recommendations are dynamically ranked using student feedback. Let h_c and n_c be the number of 'helpful' and 'not helpful' ratings for category c. "
        "The category multiplier M(c) is calculated via Bayesian smoothing with an exploration floor:"
    )
    add_para(
        "M(c) = max(0.5, (h_c + 1) / (h_c + n_c + 2))    (1)\n\n"
        "Crucially, safety-critical resources (e.g., Campus Counseling and Crisis Hotline Support) are permanently pinned to rank 1 whenever severe distress is indicated, "
        "and are mathematically exempt from demotion or feedback suppression."
    )

    add_sec_heading("E. Privacy-by-Design Architecture", level=2)
    add_para(
        "In sharp contrast to the base paper's immutable blockchain proposal, WellSense implements privacy-preserving local SQLite storage. Each user interaction "
        "is assigned a pseudonymous UUID session ID with zero personally identifying information (PII) collected. Students retain complete data sovereignty through "
        "'Reset My Feedback' and 'Delete ALL My Data' controls that purge session rows immediately."
    )

    add_sec_heading("IV. EXPERIMENTAL RESULTS & ABLATION")
    add_para(
        "The experimental evaluation was conducted on the complete 101-student survey dataset. The target variable comprises 66 'No' responses (65.3%) and 35 'Yes' responses (34.7%), "
        "establishing an empirical majority baseline accuracy of 65.3%."
    )

    add_fig(FIG_TARGET_DIST, "Fig. 1. Class distribution of self-reported depression target (N=101).")

    add_sec_heading("A. Multi-Model Benchmark Across Feature Tiers", level=2)
    add_para(
        "Table I presents the repeated nested cross-validation results across all eight classifiers and three feature tiers."
    )

    # TABLE I: Model Comparison
    table_data = [
        ["Tier", "Model", "Kind", "Accuracy", "Balanced Acc.", "F1-Score", "ROC AUC"],
        ["A", "Dummy Majority", "Baseline", "0.653 ± 0.007", "0.500 ± 0.000", "0.000 ± 0.000", "0.500 ± 0.000"],
        ["A", "Logistic Regression", "Classical", "0.719 ± 0.110", "0.690 ± 0.140", "0.560 ± 0.252", "0.753 ± 0.138"],
        ["A", "Random Forest", "Classical", "0.737 ± 0.105", "0.699 ± 0.131", "0.571 ± 0.242", "0.758 ± 0.137"],
        ["A", "Gradient Boosting", "Classical", "0.780 ± 0.101", "0.719 ± 0.128", "0.581 ± 0.269", "0.774 ± 0.115"],
        ["A", "Tuned MLP (Nested CV)", "Proposed DL", "0.786 ± 0.095", "0.739 ± 0.119", "0.633 ± 0.213", "0.760 ± 0.122"],
        ["B", "Dummy Majority", "Baseline", "0.653 ± 0.007", "0.500 ± 0.000", "0.000 ± 0.000", "0.500 ± 0.000"],
        ["B", "Logistic Regression", "Classical", "0.741 ± 0.087", "0.714 ± 0.106", "0.617 ± 0.149", "0.804 ± 0.113"],
        ["B", "Random Forest", "Classical", "0.782 ± 0.072", "0.739 ± 0.100", "0.631 ± 0.178", "0.797 ± 0.108"],
        ["B", "SVM (RBF Kernel)", "Classical", "0.753 ± 0.093", "0.715 ± 0.108", "0.606 ± 0.175", "0.762 ± 0.109"],
        ["B", "Gradient Boosting", "Classical", "0.790 ± 0.079", "0.729 ± 0.112", "0.601 ± 0.236", "0.823 ± 0.106"],
        ["B", "Initial MLP (32-16)", "Baseline DL", "0.743 ± 0.096", "0.708 ± 0.103", "0.607 ± 0.157", "0.767 ± 0.107"],
        ["B", "Tuned MLP (Nested CV)", "Deployed DL", "0.782 ± 0.085", "0.735 ± 0.111", "0.624 ± 0.213", "0.802 ± 0.109"],
        ["C", "Random Forest", "Classical", "0.790 ± 0.066", "0.745 ± 0.077", "0.654 ± 0.126", "0.830 ± 0.085"],
        ["C", "Tuned MLP (Nested CV)", "Proposed DL", "0.792 ± 0.077", "0.745 ± 0.102", "0.642 ± 0.192", "0.800 ± 0.112"],
    ]

    t1 = doc.add_table(rows=len(table_data), cols=7)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table_data):
        for j, val in enumerate(row):
            cell = t1.cell(i, j)
            cell.text = val
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(7.5 if i > 0 else 8.0)
            if i == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "E0E0E0")
            elif i % 2 == 1:
                set_cell_background(cell, "F9F9F9")
            set_cell_margins(cell, top=40, bottom=40, left=40, right=40)

    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(2)
    p_tcap.paragraph_format.space_after = Pt(6)
    r = p_tcap.add_run("TABLE I. 5x5 Repeated Nested CV Model Benchmark Across Feature Tiers.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(8.0)
    r.font.bold = True

    add_fig(FIG_MODEL_COMP, "Fig. 2. Comparative balanced accuracy across feature tiers (mean ± SD).")

    add_sec_heading("B. Paired Statistical Comparison & Honesty", level=2)
    add_para(
        "Under Tier B (the deployed feature set), the Tuned MLP achieved a balanced accuracy of 0.735 ± 0.111, while Random Forest achieved 0.739 ± 0.100. "
        "A paired fold-by-fold analysis reveals a mean difference of -0.004 (MLP higher on 9 folds, RF higher on 16 folds), demonstrating that the neural network "
        "is statistically tied with Random Forest. Furthermore, regularizing the MLP (Tuned vs Initial MLP) yielded a +0.027 gain in balanced accuracy. "
        "These findings conclusively establish that claiming superiority for deep learning over ensemble methods on small tabular cohorts is scientifically unwarranted."
    )

    add_sec_heading("C. XAI & The Marital Status Data Artifact", level=2)
    add_para(
        "Table II details the global permutation feature importance. Marital status emerged as the overwhelmingly dominant predictor, with a performance drop of 0.1877 ± 0.0928, "
        "followed by self-reported anxiety (0.0369 ± 0.0704) and CGPA band (0.0172 ± 0.0477)."
    )

    add_fig(FIG_FEAT_IMP, "Fig. 3. Global feature permutation importance on held-out test folds.")

    add_para(
        "A critical contribution of WellSense is exposing why marital status dominates: in this specific 101-student sample, exactly 16 out of 16 married students "
        "answered 'Yes' to depression. The machine learning model captures this 100% conditional distribution as a mathematical shortcut. WellSense explicitly surfaces "
        "this finding as a data artifact in the user interface rather than a genuine real-world causal relationship, preventing counselors from misinterpreting model rationale."
    )

    add_fig(FIG_CONF_MAT, "Fig. 4. Out-of-fold confusion matrix for the deployed MLP configuration.")
    add_fig(FIG_TRAIN_CURVE, "Fig. 5. Final MLP training loss convergence curve.")

    add_sec_heading("D. Adaptive Recommendation Dynamics", level=2)
    add_para(
        "Table II illustrates the closed-loop recommendation re-ranking for a representative student profile before and after receiving negative feedback for sleep suggestions "
        "and positive feedback for social connection."
    )

    demo_data = [
        ["Rank", "Baseline (No Feedback)", "Adapted (After Feedback)"],
        ["1", "Sleep Routine (sleep_routine)", "Social Connection (connect)"],
        ["2", "Screen Balance (screen_balance)", "Screen Balance (screen_balance)"],
        ["3", "Physical Movement (movement)", "Physical Movement (movement)"],
        ["4", "Social Connection (connect)", "Sleep Routine (sleep_routine)"],
    ]
    t2 = doc.add_table(rows=len(demo_data), cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(demo_data):
        for j, val in enumerate(row):
            cell = t2.cell(i, j)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(8.0)
            if i == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "E0E0E0")
            set_cell_margins(cell, top=30, bottom=30, left=40, right=40)

    p_t2cap = doc.add_paragraph()
    p_t2cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2cap.paragraph_format.space_after = Pt(6)
    r = p_t2cap.add_run("TABLE II. Recommendation Ranking Adaptation Before and After Feedback.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(8.0)
    r.font.bold = True

    add_sec_heading("V. SYSTEM IMPLEMENTATION & VERIFICATION")
    add_para(
        "The WellSense software system was developed in Python 3.14 using scikit-learn, Streamlit, and SQLite. The web interface comprises six dedicated views: "
        "Home, Assessment, Prediction Results, Personalized Recommendations, Feedback & History, and About & Privacy. The entire pipeline is verified by a 30-test unit suite "
        "and a headless Streamlit AppTest smoke harness validating standalone page loads, validation boundaries (e.g., rejecting age < 16 and > 60), model inference, and SQLite session purging. "
        "The full application is open-source and publicly hosted on GitHub at https://github.com/sudheshna03/WellSense."
    )

    add_sec_heading("VI. LIMITATIONS & ETHICS")
    add_para(
        "Several limitations govern our findings: (1) Sample Size: The evaluation is based on 101 records from a single cohort; (2) Self-Report Construct: The target reflects a binary "
        "questionnaire item rather than a clinical psychiatric evaluation; (3) Demographic Imbalance: The sample is predominantly female (75%) and undergraduate, limiting generalizability; "
        "(4) Absence of Longitudinal Tracking: Mental health fluctuates dynamically over academic semesters; and (5) Non-Clinical Scope: WellSense is strictly an educational reflection tool. "
        "Prominent disclaimers across all interface views explicitly state that predictions do not constitute medical diagnoses."
    )

    add_sec_heading("VII. CONCLUSION")
    add_para(
        "This paper presented WellSense, an explainable, privacy-preserving, and feedback-adaptive framework extending machine learning baselines for student wellbeing support. "
        "By applying leak-free repeated nested cross-validation, we established that a tuned MLP (balanced accuracy: 0.735 ± 0.111) is statistically on par with Random Forest (0.739 ± 0.100), "
        "demonstrating that prior claims of 95.6% accuracy are non-reproducible on the public survey cohort. WellSense bridges the gap between passive risk prediction and proactive support "
        "through local feature explanations, closed-loop habit recommendations, and a local privacy-by-design architecture. Future work will expand evaluations to multi-institutional cohorts "
        "and conduct prospective longitudinal user studies."
    )

    add_sec_heading("REFERENCES")
    refs = [
        "[1] M. D. Nath, M. K. U. Ahamed, O. Ahmed, T. Ahmed, S. Roy, and M. N. Uddin, 'Smart web interface for student mental health prediction using machine learning with blockchain technology,' Neuroscience Informatics, vol. 5, no. 4, art. no. 100236, 2025.",
        "[2] A. Baba and K. Bunji, 'Prediction of mental health problem using annual student health survey: Machine learning approach,' JMIR Mental Health, vol. 10, art. no. e42420, 2023.",
        "[3] N. Dhariwal, N. Sengupta, M. Madiajagan, et al., 'A pilot study on AI-driven approaches for classification of mental health disorders,' Front. Human Neurosci., vol. 18, art. no. 1376338, 2024.",
        "[4] L. K. Ramasamy, F. Khan, S. Joghee, J. Dempere, and P. Garg, 'Forecast of students' mental health combining an artificial intelligence technique and fuzzy inference system,' in Proc. IEEE AUTOCOM, 2024, pp. 85-90.",
        "[5] shariful07, 'Student Mental Health Dataset,' Kaggle, 2023. [Online]. Available: https://www.kaggle.com/datasets/shariful07/student-mental-health",
        "[6] G. S. Collins, K. G. M. Moons, P. Dhiman, et al., 'TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods,' BMJ, vol. 385, art. no. e078378, 2024.",
        "[7] L. Breiman, 'Random forests,' Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.",
        "[8] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Adv. Neural Inf. Process. Syst. (NeurIPS), 2017, pp. 4765-4774.",
        "[9] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.2)
        p_ref.paragraph_format.first_line_indent = Inches(-0.2)
        p_ref.paragraph_format.space_after = Pt(3)
        run = p_ref.add_run(r)
        run.font.name = "Times New Roman"
        run.font.size = Pt(8.0)

    doc.save(str(DOCX_PATH))
    print(f"  [OK] Word document saved to: {DOCX_PATH}")


def set_cell_background(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=40, bottom=40, left=40, right=40):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(m)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


# ==============================================================================
# 2. PDF GENERATION VIA HEADLESS EDGE
# ==============================================================================
def create_pdf():
    print("--> Generating IEEE-styled PDF Document (.pdf)...")

    def b64(img_path):
        if img_path.exists():
            return "data:image/png;base64," + base64.b64encode(img_path.read_bytes()).decode("utf-8")
        return ""

    img_target = b64(FIG_TARGET_DIST)
    img_model = b64(FIG_MODEL_COMP)
    img_feat = b64(FIG_FEAT_IMP)
    img_conf = b64(FIG_CONF_MAT)
    img_train = b64(FIG_TRAIN_CURVE)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>WellSense Research Paper</title>
<style>
  @page {{
    size: letter;
    margin: 0.65in 0.65in 0.65in 0.65in;
  }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 9.5pt;
    line-height: 1.15;
    color: #111;
    margin: 0;
    padding: 0;
  }}
  .title-area {{
    text-align: center;
    margin-bottom: 12px;
  }}
  h1.title {{
    font-size: 17pt;
    font-weight: bold;
    margin: 0 0 4px 0;
    line-height: 1.15;
  }}
  .subtitle {{
    font-size: 10.5pt;
    font-style: italic;
    color: #444;
    margin: 0 0 10px 0;
  }}
  .author-block {{
    font-size: 10pt;
    font-weight: bold;
    margin-bottom: 2px;
  }}
  .affil-block {{
    font-size: 9pt;
    font-style: italic;
    color: #333;
    margin-bottom: 14px;
  }}
  .abstract-box {{
    margin: 0 0.25in 14px 0.25in;
    text-align: justify;
    font-size: 8.8pt;
    line-height: 1.15;
  }}
  .abstract-label {{
    font-weight: bold;
    font-style: italic;
  }}
  .columns {{
    column-count: 2;
    column-gap: 0.35in;
    text-align: justify;
  }}
  h2.sec-h {{
    font-size: 10pt;
    font-weight: bold;
    text-transform: uppercase;
    margin: 10px 0 3px 0;
    border-bottom: 0.5pt solid #888;
    padding-bottom: 1px;
    break-after: avoid;
  }}
  h3.subsec-h {{
    font-size: 9.5pt;
    font-weight: bold;
    font-style: italic;
    margin: 6px 0 2px 0;
    break-after: avoid;
  }}
  p {{
    margin: 0 0 6px 0;
    text-indent: 0.15in;
  }}
  p.no-indent {{
    text-indent: 0;
  }}
  .fig-container {{
    text-align: center;
    margin: 8px 0;
    break-inside: avoid;
  }}
  .fig-container img {{
    max-width: 100%;
    height: auto;
    border: 0.5pt solid #ccc;
  }}
  .caption {{
    font-size: 8pt;
    font-style: italic;
    margin-top: 3px;
    text-align: center;
  }}
  table.ieee-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.5pt;
    margin: 8px 0;
    break-inside: avoid;
  }}
  table.ieee-table th, table.ieee-table td {{
    border: 0.5pt solid #bbb;
    padding: 3px 4px;
    text-align: center;
  }}
  table.ieee-table th {{
    background-color: #e8e8e8;
    font-weight: bold;
  }}
  table.ieee-table tr:nth-child(even) {{
    background-color: #f9f9f9;
  }}
  .table-cap {{
    font-size: 7.8pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 3px;
  }}
  .ref-list {{
    font-size: 7.8pt;
    padding-left: 0.2in;
    margin: 0;
  }}
  .ref-list li {{
    margin-bottom: 4px;
    text-indent: -0.15in;
  }}
</style>
</head>
<body>

<div class="title-area">
  <h1 class="title">WellSense: An Explainable, Privacy-Preserving, and Feedback-Adaptive Framework for Student Wellbeing Support</h1>
  <div class="subtitle">A Methodological Audit and Human-Centered System Extension of Machine Learning Baselines</div>
  <div class="author-block">Sudheshna Devi</div>
  <div class="affil-block">
    Department of Computer Science and Engineering<br>
    Prasad V. Potluri Siddhartha Institute of Technology, Vijayawada, India<br>
    sudheshnat29@gmail.com
  </div>
</div>

<div class="abstract-box">
  <span class="abstract-label">Abstract—</span><strong>Student mental health systems increasingly rely on predictive machine learning to detect psychological distress. However, existing systems—exemplified by the foundational study of Nath et al. (Neuroscience Informatics, 2025)—suffer from acute architectural limitations: they terminate at black-box probability scores without actionable guidance, report inflated single-split accuracies (95.6%) that do not hold under rigorous leak-free cross-validation, and propose permanently storing sensitive student mental health responses on public immutable blockchains. To address these critical gaps, this paper introduces WellSense: an explainable, privacy-preserving, and feedback-adaptive decision-support prototype. WellSense benchmarks a tuned Multi-Layer Perceptron (MLP) against seven classical classifiers under a 5x5 repeated nested cross-validation protocol (25 outer folds) across three isolated feature tiers. Empirical evaluation shows that under leak-free nested CV, the tuned MLP achieves a balanced accuracy of 0.735 ± 0.111 (accuracy: 0.782 ± 0.085, ROC AUC: 0.802 ± 0.109), proving to be statistically tied with Random Forest (0.739 ± 0.100, paired difference: -0.004). To eliminate black-box opacity, WellSense incorporates global permutation importance on held-out folds and local occlusion feature attribution, uncovering a severe dataset artifact where marital status disproportionately dominates predictions (importance: 0.1877 ± 0.0928) due to a 16/16 correlation in the survey sample. Bridging the gap between prediction and support, WellSense introduces a transparent, non-clinical recommendation engine coupled with a Bayesian-smoothed feedback loop that dynamically re-ranks lifestyle suggestions while strictly pinning safety resources. Finally, the system rejects public blockchain storage in favor of a privacy-first, local SQLite architecture with pseudonymous UUID sessions and on-demand data deletion. Framed strictly as an educational support aid rather than a clinical diagnostic instrument, WellSense provides a reproducible, methodologically honest paradigm for student wellbeing informatics.</strong>
  <br><br>
  <span class="abstract-label">Keywords—</span>Student Mental Health, Machine Learning, Multi-Layer Perceptron, Explainable AI (XAI), Feature Occlusion, Feedback Adaptation, Decision Support, Health Informatics, Privacy-by-Design, Research Integrity.
</div>

<div class="columns">

<h2 class="sec-h">I. Introduction</h2>
<p>University students experience acute psychological challenges arising from compounding academic workloads, societal pressures, and the personal transition into independent adulthood. While higher education institutions frequently establish campus healthcare and counseling centers, pervasive social stigma and resource constraints frequently delay access to timely assistance. In response, data-driven machine learning (ML) models have emerged as an attractive solution for screening mental distress from self-reported survey indicators.</p>
<p>A prominent recent contribution by Nath et al. [1], published in <em>Neuroscience Informatics</em> (Elsevier, 2025), proposed a web-based prediction system combining twelve ML algorithms, a Streamlit interface, and an Ethereum-based blockchain storage module, reporting a headline Random Forest accuracy of 95.6%. While their work demonstrates commendable engineering ambition, our critical analysis reveals several vital methodological and architectural limitations:</p>
<p class="no-indent">• <em>Evaluation Rigor</em>: Their 95.6% result relied on a single 70/30 train/test split, lacking repeated cross-validation or standard deviation reporting.</p>
<p class="no-indent">• <em>Data Leakage</em>: Their feature set incorporated variables such as professional treatment-seeking and overlapping acute clinical indicators that co-occur contemporaneously with depression.</p>
<p class="no-indent">• <em>The Prediction-Action Gap</em>: Their system functions as a predictive black box, generating a probability score without offering actionable, personalized coping guidance.</p>
<p class="no-indent">• <em>Privacy & Ethics</em>: Storing sensitive student mental health responses on an immutable public blockchain ledger introduces severe regulatory risks under GDPR and fails to support the fundamental 'right to be forgotten.'</p>
<p>To resolve these challenges, this paper presents <strong>WellSense</strong>, an end-to-end, privacy-preserving, and explainable decision-support prototype. WellSense introduces: (1) leak-free repeated nested cross-validation benchmarking of a tuned neural network (MLP); (2) feature tiering to isolate target leakage; (3) Explainable AI (XAI) combining global permutation and local occlusion attribution; (4) a closed-loop recommendation engine that adapts to student feedback; and (5) a privacy-first local SQLite architecture with pseudonymous UUID sessions.</p>

<h2 class="sec-h">II. Base Paper Audit & Related Work</h2>
<p>Predictive modeling of student mental health has gained substantial traction. Baba and Bunji [2] examined annual health surveys across 3,561 undergraduates, demonstrating the utility of repeated survey data while observing that model weights fail to generalize across distinct academic cohorts. Dhariwal et al. [3] and Ramasamy et al. [4] investigated multi-model ensembles for student depression detection, yet similarly terminated their workflows at point-in-time classification.</p>
<p>The base paper by Nath et al. [1] represents the closest prior art. They trained 12 classifiers on 500 composite records, claiming 95.6% accuracy for a Random Forest. However, an in-depth audit reveals that their confusion matrices (64 TN, 4 FP, 1 FN, 32 TP) sum to exactly 101 test records, matching the public Kaggle 'Student Mental Health' dataset [5] rather than their stated 500-student cohort. Furthermore, feature importance in their study placed heavy reliance on treatment-seeking and anxiety. In contrast, responsible ML guidelines, such as TRIPOD+AI [6], mandate nested validation, leakage-aware feature tiering, transparent uncertainty reporting, and strict separation between exploratory baselines and clinical claims.</p>

<h2 class="sec-h">III. WellSense System Architecture</h2>
<p>WellSense is structured into four decoupled layers: (A) Preprocessing and Leakage-Aware Tiering, (B) Neural Network and Baseline Classifiers, (C) Explainability Layer, (D) Feedback-Adaptive Recommendation Engine, and (E) Privacy-Preserving Storage.</p>

<h3 class="subsec-h">A. Preprocessing & Feature Tiering</h3>
<p>To evaluate model sensitivity to feature leakage, WellSense structures predictors into three isolated tiers:</p>
<p class="no-indent">• <em>Tier A (Demographic & Academic)</em>: Gender, Age, Year of Study, CGPA band, and Grouped Course Category (engineering/IT, health sciences, islamic studies, business/law, other).</p>
<p class="no-indent">• <em>Tier B (Primary Deployed Tier)</em>: Tier A plus self-reported psychological indicators (Anxiety, Panic Attacks, and Marital Status). Treatment-seeking is strictly excluded to prevent target leakage.</p>
<p class="no-indent">• <em>Tier C (Diagnostic Overlap Tier)</em>: All features including treatment-seeking, evaluated solely for ablation comparison.</p>
<p>All preprocessing operations (median imputation for age, mode imputation for categoricals, and one-hot encoding) are encapsulated in scikit-learn Pipelines and fitted strictly on training folds.</p>

<h3 class="subsec-h">B. Nested Cross-Validation & Model Zoo</h3>
<p>WellSense benchmarks eight supervised architectures under 5x5 Repeated Stratified Cross-Validation (25 outer folds): Dummy Majority Baseline, Logistic Regression, Decision Tree, Random Forest (200 trees), Support Vector Classifier (RBF kernel), Gradient Boosting, Initial MLP (32-16 architecture, alpha=1e-4), and a Tuned MLP. The Tuned MLP undergoes inner 3-fold CV tuning across hidden layer configurations ((8,), (16,), (32, 16)), L2 regularization penalties (alpha from 0.001 to 1.0), and iteration budgets (200 to 600).</p>

<h3 class="subsec-h">C. Explainable AI (XAI) Framework</h3>
<p>WellSense implements a two-fold interpretability strategy: (1) Global Permutation Importance evaluated across held-out test folds over 20 shuffle iterations to quantify drops in balanced accuracy; and (2) Local Feature Occlusion where each feature is systematically substituted with its cohort median/mode during inference, revealing whether that specific answer elevated (↑) or reduced (↓) the estimated distress probability.</p>

<h3 class="subsec-h">D. Adaptive Recommendation Engine</h3>
<p>WellSense captures six optional lifestyle indicators: sleep hours (0–14), longest uninterrupted study stretch (0–14), physical activity days (0–7), screen time (0–18), social support score (1–5), and study planning difficulty (1–5). A rule-based engine generates non-clinical, actionable habits.</p>
<p>Recommendations are dynamically ranked using student feedback. Let <em>h_c</em> and <em>n_c</em> denote helpful and not helpful counts for category <em>c</em>. The category multiplier <em>M(c)</em> is calculated via Bayesian smoothing with an exploration floor:</p>
<p style="text-align:center; text-indent:0;"><em>M(c) = max(0.5, (h_c + 1) / (h_c + n_c + 2))</em> &nbsp;&nbsp;&nbsp; (1)</p>
<p>Crucially, safety-critical resources (e.g., Campus Counseling and Crisis Hotline Support) are permanently pinned to rank 1 whenever severe distress is indicated, and are mathematically exempt from demotion.</p>

<h3 class="subsec-h">E. Privacy-by-Design Architecture</h3>
<p>In sharp contrast to public blockchain storage, WellSense implements a local SQLite database with pseudonymous UUID sessions. Students retain full data sovereignty through 'Reset My Feedback' and 'Delete ALL My Data' controls that purge session rows immediately.</p>

<h2 class="sec-h">IV. Experimental Results & Analysis</h2>
<p>The evaluation was conducted on the complete 101-student survey dataset. The target variable comprises 66 'No' responses (65.3%) and 35 'Yes' responses (34.7%), establishing a majority baseline accuracy of 65.3%.</p>

<div class="fig-container">
  <img src="{img_target}" alt="Target Distribution">
  <div class="caption">Fig. 1. Class distribution of self-reported depression target (N=101).</div>
</div>

<div class="table-cap">TABLE I. 5x5 Repeated Nested CV Benchmark Across Feature Tiers</div>
<table class="ieee-table">
  <tr>
    <th>Tier</th><th>Model</th><th>Kind</th><th>Accuracy</th><th>Balanced Acc.</th><th>F1-Score</th><th>ROC AUC</th>
  </tr>
  <tr><td>A</td><td>Dummy Majority</td><td>Baseline</td><td>0.653 ± 0.007</td><td>0.500 ± 0.000</td><td>0.000 ± 0.000</td><td>0.500 ± 0.000</td></tr>
  <tr><td>A</td><td>Logistic Regression</td><td>Classical</td><td>0.719 ± 0.110</td><td>0.690 ± 0.140</td><td>0.560 ± 0.252</td><td>0.753 ± 0.138</td></tr>
  <tr><td>A</td><td>Random Forest</td><td>Classical</td><td>0.737 ± 0.105</td><td>0.699 ± 0.131</td><td>0.571 ± 0.242</td><td>0.758 ± 0.137</td></tr>
  <tr><td>A</td><td>Gradient Boosting</td><td>Classical</td><td>0.780 ± 0.101</td><td>0.719 ± 0.128</td><td>0.581 ± 0.269</td><td>0.774 ± 0.115</td></tr>
  <tr><td>A</td><td>Tuned MLP (Nested)</td><td>DL</td><td>0.786 ± 0.095</td><td>0.739 ± 0.119</td><td>0.633 ± 0.213</td><td>0.760 ± 0.122</td></tr>
  <tr><td>B</td><td>Dummy Majority</td><td>Baseline</td><td>0.653 ± 0.007</td><td>0.500 ± 0.000</td><td>0.000 ± 0.000</td><td>0.500 ± 0.000</td></tr>
  <tr><td>B</td><td>Logistic Regression</td><td>Classical</td><td>0.741 ± 0.087</td><td>0.714 ± 0.106</td><td>0.617 ± 0.149</td><td>0.804 ± 0.113</td></tr>
  <tr><td>B</td><td>Random Forest</td><td>Classical</td><td>0.782 ± 0.072</td><td>0.739 ± 0.100</td><td>0.631 ± 0.178</td><td>0.797 ± 0.108</td></tr>
  <tr><td>B</td><td>SVM (RBF Kernel)</td><td>Classical</td><td>0.753 ± 0.093</td><td>0.715 ± 0.108</td><td>0.606 ± 0.175</td><td>0.762 ± 0.109</td></tr>
  <tr><td>B</td><td>Gradient Boosting</td><td>Classical</td><td>0.790 ± 0.079</td><td>0.729 ± 0.112</td><td>0.601 ± 0.236</td><td>0.823 ± 0.106</td></tr>
  <tr><td>B</td><td>Initial MLP (32-16)</td><td>DL</td><td>0.743 ± 0.096</td><td>0.708 ± 0.103</td><td>0.607 ± 0.157</td><td>0.767 ± 0.107</td></tr>
  <tr><td>B</td><td>Tuned MLP (Deployed)</td><td>DL</td><td>0.782 ± 0.085</td><td>0.735 ± 0.111</td><td>0.624 ± 0.213</td><td>0.802 ± 0.109</td></tr>
  <tr><td>C</td><td>Random Forest</td><td>Classical</td><td>0.790 ± 0.066</td><td>0.745 ± 0.077</td><td>0.654 ± 0.126</td><td>0.830 ± 0.085</td></tr>
  <tr><td>C</td><td>Tuned MLP (Nested)</td><td>DL</td><td>0.792 ± 0.077</td><td>0.745 ± 0.102</td><td>0.642 ± 0.192</td><td>0.800 ± 0.112</td></tr>
</table>

<div class="fig-container">
  <img src="{img_model}" alt="Model Comparison">
  <div class="caption">Fig. 2. Comparative balanced accuracy across feature tiers (mean ± SD).</div>
</div>

<h3 class="subsec-h">A. Paired Statistical Comparison & Honesty</h3>
<p>Under Tier B, the Tuned MLP achieved a balanced accuracy of 0.735 ± 0.111, while Random Forest achieved 0.739 ± 0.100. A paired fold-by-fold analysis reveals a mean difference of -0.004 (MLP higher on 9 folds, RF higher on 16 folds), demonstrating that the neural network is statistically tied with Random Forest. Furthermore, regularizing the MLP (Tuned vs Initial MLP) yielded a +0.027 gain in balanced accuracy. These findings establish that claiming superiority for deep learning over ensemble methods on small tabular cohorts is scientifically unwarranted.</p>

<h3 class="subsec-h">B. XAI & The Marital Status Data Artifact</h3>
<p>Global permutation feature importance revealed that Marital status was overwhelmingly dominant, causing a balanced accuracy drop of 0.1877 ± 0.0928, followed by anxiety (0.0369 ± 0.0704) and CGPA band (0.0172 ± 0.0477).</p>

<div class="fig-container">
  <img src="{img_feat}" alt="Feature Importance">
  <div class="caption">Fig. 3. Global feature permutation importance on held-out test folds.</div>
</div>

<p>A crucial contribution of WellSense is exposing why marital status dominates: in this 101-student sample, exactly 16 out of 16 married students answered 'Yes' to depression. The machine learning model captures this 100% conditional distribution as a mathematical shortcut. WellSense explicitly surfaces this finding as a data artifact in the user interface rather than a genuine real-world causal relationship.</p>

<div class="fig-container">
  <img src="{img_conf}" alt="Confusion Matrix">
  <div class="caption">Fig. 4. Out-of-fold confusion matrix for the deployed MLP configuration.</div>
</div>

<div class="fig-container">
  <img src="{img_train}" alt="Training Loss Curve">
  <div class="caption">Fig. 5. Final MLP training loss convergence curve.</div>
</div>

<h3 class="subsec-h">C. Adaptive Recommendation Dynamics</h3>
<p>Table II illustrates closed-loop recommendation re-ranking for a representative student profile before and after receiving negative feedback for sleep suggestions and positive feedback for social connection.</p>

<div class="table-cap">TABLE II. Recommendation Ranking Adaptation Before and After Feedback</div>
<table class="ieee-table">
  <tr><th>Rank</th><th>Baseline (No Feedback)</th><th>Adapted (After Feedback)</th></tr>
  <tr><td>1</td><td>Sleep Routine (sleep_routine)</td><td>Social Connection (connect)</td></tr>
  <tr><td>2</td><td>Screen Balance (screen_balance)</td><td>Screen Balance (screen_balance)</td></tr>
  <tr><td>3</td><td>Physical Movement (movement)</td><td>Physical Movement (movement)</td></tr>
  <tr><td>4</td><td>Social Connection (connect)</td><td>Sleep Routine (sleep_routine)</td></tr>
</table>

<h2 class="sec-h">V. System Implementation & Verification</h2>
<p>WellSense was developed in Python 3.14 using scikit-learn, Streamlit, and SQLite. The web interface comprises six dedicated views: Home, Assessment, Prediction Results, Personalized Recommendations, Feedback & History, and About & Privacy. The entire pipeline is verified by a 30-test unit suite and a headless Streamlit AppTest smoke harness validating standalone page loads, validation boundaries (rejecting age < 16 and > 60), model inference, and SQLite session purging. The full application is open-source and publicly hosted on GitHub at https://github.com/sudheshna03/WellSense.</p>

<h2 class="sec-h">VI. Limitations & Ethical Considerations</h2>
<p>Several limitations govern our findings: (1) Sample Size: The evaluation is based on 101 records; (2) Self-Report Construct: The target reflects a binary questionnaire item rather than a clinical evaluation; (3) Demographic Imbalance: The sample is predominantly female (75%) and undergraduate; (4) Absence of Longitudinal Tracking: Mental health fluctuates dynamically over semesters; and (5) Non-Clinical Scope: WellSense is strictly an educational reflection tool with non-clinical disclaimers prominently maintained across all views.</p>

<h2 class="sec-h">VII. Conclusion</h2>
<p>This paper presented WellSense, an explainable, privacy-preserving, and feedback-adaptive framework extending machine learning baselines for student wellbeing support. Applying leak-free repeated nested cross-validation established that a tuned MLP (balanced accuracy: 0.735 ± 0.111) is statistically on par with Random Forest (0.739 ± 0.100), demonstrating that prior claims of 95.6% accuracy are non-reproducible on the public survey cohort. WellSense bridges the gap between passive risk prediction and proactive support through local feature explanations, closed-loop habit recommendations, and a local privacy-by-design architecture. Future work will expand evaluations to multi-institutional cohorts and conduct prospective longitudinal user studies.</p>

<h2 class="sec-h">References</h2>
<ol class="ref-list">
  <li>M. D. Nath, M. K. U. Ahamed, O. Ahmed, T. Ahmed, S. Roy, and M. N. Uddin, "Smart web interface for student mental health prediction using machine learning with blockchain technology," <em>Neuroscience Informatics</em>, vol. 5, no. 4, art. no. 100236, 2025.</li>
  <li>A. Baba and K. Bunji, "Prediction of mental health problem using annual student health survey: Machine learning approach," <em>JMIR Mental Health</em>, vol. 10, art. no. e42420, 2023.</li>
  <li>N. Dhariwal, N. Sengupta, M. Madiajagan, et al., "A pilot study on AI-driven approaches for classification of mental health disorders," <em>Front. Human Neurosci.</em>, vol. 18, art. no. 1376338, 2024.</li>
  <li>L. K. Ramasamy, F. Khan, S. Joghee, J. Dempere, and P. Garg, "Forecast of students' mental health combining an artificial intelligence technique and fuzzy inference system," in <em>Proc. IEEE AUTOCOM</em>, 2024, pp. 85-90.</li>
  <li>shariful07, "Student Mental Health Dataset," Kaggle, 2023. [Online]. Available: https://www.kaggle.com/datasets/shariful07/student-mental-health</li>
  <li>G. S. Collins, K. G. M. Moons, P. Dhiman, et al., "TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods," <em>BMJ</em>, vol. 385, art. no. e078378, 2024.</li>
  <li>L. Breiman, "Random forests," <em>Machine Learning</em>, vol. 45, no. 1, pp. 5-32, 2001.</li>
  <li>S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in <em>Adv. Neural Inf. Process. Syst. (NeurIPS)</em>, 2017, pp. 4765-4774.</li>
  <li>F. Pedregosa et al., "Scikit-learn: Machine learning in Python," <em>Journal of Machine Learning Research</em>, vol. 12, pp. 2825-2830, 2011.</li>
</ol>

</div>

</body>
</html>"""

    HTML_PATH.write_text(html_content, encoding="utf-8")
    print(f"  [OK] HTML written to: {HTML_PATH}")

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not Path(edge_bin).exists():
        edge_bin = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    cmd = [
        edge_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={PDF_PATH}",
        str(HTML_PATH),
    ]

    subprocess.run(cmd, check=True)
    print(f"  [OK] PDF document saved to: {PDF_PATH}")


def main():
    create_docx()
    create_pdf()
    print("\n=======================================================")
    print(f"  SUCCESS! Research paper generated in both formats:")
    print(f"  1. Word Doc: {DOCX_PATH}")
    print(f"  2. PDF Doc:  {PDF_PATH}")
    print("=======================================================")


if __name__ == "__main__":
    main()
