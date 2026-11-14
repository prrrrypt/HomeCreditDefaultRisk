# Day 13 — Final Held-Out Model Evaluation

## 1. Executive Summary

This phase conducted the final held-out evaluation of the LightGBM credit risk classification model and Logistic Regression benchmark developed during Days 5–12.

The evaluation used the original test partition of 61,503 applications, which had been excluded from model training, hyperparameter selection, threshold optimization, and preceding model analyses.

The objective was to assess predictive generalization, probability calibration, statistical uncertainty, and performance of previously selected hypothetical screening strategies.

## 2. Evaluation Protocol

The original stratified dataset split was preserved:

| Partition | Applications | Purpose |
|---|---:|---|
| Training | 184,506 | Model fitting |
| Validation | 61,502 | Model development and policy exploration |
| Test | 61,503 | Final held-out evaluation |

The trained Day 6 LightGBM model and fitted preprocessing pipeline were loaded without retraining.

The Logistic Regression benchmark was reproduced using the original training partition and previously established model configuration.

The final evaluation used a probability threshold of 0.06 and a fixed screening capacity of 20%, both determined before test-set evaluation.

## 3. Final Model Performance

| Metric | Logistic Regression | LightGBM |
|---|---:|---:|
| Test ROC-AUC | [Result] | [Result] |
| Test Average Precision | [Result] | [Result] |
| Test Brier Score | [Result] | [Result] |

### Validation-to-Test Generalization

[Compare each model's validation and test performance.]

[Discuss whether the differences suggest reasonable generalization or potential overfitting.]

## 4. Statistical Uncertainty

Approximate 95% bootstrap confidence intervals were calculated for ROC-AUC, Average Precision, and Brier Score.

[Insert LightGBM confidence intervals.]

A paired bootstrap was used to compare LightGBM and Logistic Regression using the same test observations.

[Interpret the confidence intervals for the model performance differences.]

## 5. Frozen Probability Threshold Evaluation

The previously selected probability threshold of 0.06 was applied without adjustment.

| Metric | Test Result |
|---|---:|
| Applications Reviewed | [Result] |
| Review Rate | [Result] |
| True Positives | [Result] |
| False Positives | [Result] |
| False Negatives | [Result] |
| Precision | [Result] |
| Recall | [Result] |
| Hypothetical Modeled Cost | [Result] |

The cost model assumed 25 units per review and 500 units per missed positive case.

These are illustrative assumptions and not measured financial losses.

## 6. Fixed-Capacity Screening

The highest-scoring 20% of test applications were selected using a strict maximum capacity of 12,300 applications.

| Metric | Test Result |
|---|---:|
| Applicants Reviewed | [Result] |
| Positive Cases Captured | [Result] |
| Precision | [Result] |
| Recall | [Result] |
| Lift | [Result] |
| Hypothetical Modeled Cost | [Result] |

[Compare with the previously reported validation screening results.]

## 7. Risk Decile Performance

[Report the observed repayment-difficulty rate and lift in the highest-risk test decile.]

[Describe whether observed rates generally increase across score deciles.]

[Compare predicted and observed rates as a calibration check.]

## 8. Final Assessment

[State whether LightGBM maintained its advantage over Logistic Regression.]

[Summarize the evidence for or against model generalization.]

[Identify the remaining limitations that prevent operational deployment.]

## 9. Limitations

- The dataset reflects historical application outcomes rather than a live lending environment.
- Random stratified splitting does not establish robustness to future temporal changes.
- Model performance may vary across populations, economic conditions, and data providers.
- SHAP explanations identify model attribution, not causal determinants of repayment difficulty.
- The hypothetical screening-cost model does not establish actual financial benefit.
- Feature availability, proxy discrimination, fairness, calibration stability, and regulatory compliance require additional validation.

The held-out test results provide a final assessment of the frozen modeling process; they do not establish production suitability.

## 10. Next Steps — Day 14

The final phase will consolidate the portfolio, update the README and Streamlit dashboard with clearly labeled test results, validate notebook reproducibility, and prepare a polished project presentation.

**Tools:** Python, LightGBM, scikit-learn, pandas, NumPy, DuckDB, matplotlib.