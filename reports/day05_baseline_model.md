# Day 5 — Baseline Credit Risk Modeling & Performance Evaluation

## 1. Executive Summary

This phase established a baseline machine learning framework for predicting repayment difficulties using financial application data and engineered historical credit features from the Home Credit Default Risk dataset.

A Logistic Regression classifier was developed and benchmarked against a Dummy Classifier to evaluate whether borrower financial characteristics provide meaningful predictive information.

The analysis used stratified training, validation, and test splits, preprocessing pipelines, and multiple classification metrics to assess model performance on an imbalanced dataset.

**Key findings:**

- Logistic Regression achieved a validation ROC-AUC of **0.7441**, substantially outperforming the dummy baseline of 0.5000.
- Average Precision improved from **0.0807 to 0.2208**, representing approximately **2.74 times the baseline performance**.
- The model achieved a Brier Score of **0.0688**, compared with 0.0742 for the dummy classifier.
- At the default 0.50 threshold, the model achieved 52.38% precision but only 0.66% recall, identifying very few positive cases.
- Lowering the classification threshold to 0.10 increased recall to 60.1%, demonstrating the importance of threshold selection in risk screening.

Overall, the Logistic Regression model demonstrated useful predictive discrimination, while threshold analysis highlighted substantial trade-offs between identifying potential repayment difficulties and incorrectly flagging applicants.

## 2. Dataset and Experimental Design

The modeling dataset contains 307,511 labeled applications, including financial application characteristics and aggregated historical credit bureau features engineered during Day 4.

Stratified random sampling was used to maintain the original positive-class distribution across training, validation, and test subsets.

| Dataset | Applications | Positive Rate |
|---|---:|---:|
| Training | 184,506 | 8.07% |
| Validation | 61,502 | 8.07% |
| Test | 61,503 | 8.07% |

The data was allocated using a 60% training, 20% validation, and 20% test split.

The held-out test set was reserved for final model evaluation and was not used in the reported Day 5 performance comparisons.

## 3. Model Development and Preprocessing

Two classification approaches were evaluated.

**Dummy Classifier:** Served as a benchmark using the training-set class distribution without distinguishing individual applicants by financial characteristics.

**Logistic Regression:** Served as an interpretable baseline predictive model estimating the probability of repayment difficulties from application-level and historical credit information.

Numerical predictors underwent median imputation and standardization, while categorical predictors were processed through imputation and one-hot encoding.

Scikit-learn preprocessing pipelines were used to fit transformations on training data, preventing validation-set information from influencing preprocessing parameters.

The model incorporated financial characteristics, credit exposure indicators, employment information, external-source variables, and aggregated bureau credit history features.

## 4. Validation Model Performance

| Metric | Dummy Baseline | Logistic Regression |
|---|---:|---:|
| ROC-AUC | 0.5000 | 0.7441 |
| Average Precision | 0.0807 | 0.2208 |
| Brier Score | 0.0742 | 0.0688 |
| Precision (threshold = 0.50) | 0.0000 | 0.5238 |
| Recall (threshold = 0.50) | 0.0000 | 0.0066 |
| Applicants Flagged | 0 | 63 |

### 4.1 ROC-AUC Analysis

Logistic Regression achieved a ROC-AUC of 0.7441, compared with 0.5000 for the dummy baseline.

The improvement of 0.2441 demonstrates that the model can distinguish between applicants with and without recorded repayment difficulties considerably better than random ranking.

A ROC-AUC of 0.7441 indicates that, for a randomly selected positive and negative case, the model assigns a higher risk score to the positive case approximately 74.41% of the time, accounting for ties.

The ROC curve showed a substantial improvement over the diagonal random-classification reference, although classification errors remain.

### 4.2 Precision-Recall Analysis

The model achieved an Average Precision score of 0.2208, compared with the dummy baseline of 0.0807.

This represents approximately a 2.74-fold improvement over the positive-class prevalence benchmark.

The precision-recall curve demonstrates that precision generally declines as recall increases.

At more selective thresholds, the model can identify a smaller group of applicants with relatively high positive-label prevalence. However, capturing a larger proportion of positive cases requires flagging more applicants, including those without recorded repayment difficulties.

These results are particularly relevant because the dataset has an imbalanced target distribution, with only 8.07% positive cases.

### 4.3 Probability Prediction Performance

Logistic Regression achieved a Brier Score of 0.0688, compared with 0.0742 for the dummy classifier.

The lower Brier Score indicates improved overall squared-error performance for predicted probabilities.

However, this result alone does not establish that the model is well calibrated. Calibration curves and observed-versus-predicted risk comparisons will be necessary in later stages.

## 5. Classification Threshold Analysis

**Objective:** Evaluate how classification thresholds influence the model's ability to identify repayment difficulties while controlling the number of applications flagged.

| Threshold | Applicants Flagged | Precision | Recall | False Positives | False Negatives |
|---|---:|---:|---:|---:|---:|
| 0.05 | 35,068 | 12.0% | 84.4% | 30,876 | 773 |
| 0.10 | 16,566 | 18.0% | 60.1% | 13,583 | 1,982 |
| 0.15 | 8,365 | 23.4% | 39.5% | 6,404 | 3,004 |
| 0.20 | 4,426 | 28.5% | 25.4% | 3,164 | 3,703 |
| 0.30 | 1,222 | 36.6% | 9.0% | 775 | 4,518 |
| 0.50 | 63 | 52.4% | 0.7% | 30 | 4,932 |

### 5.1 Default Threshold: 0.50

At the conventional 0.50 classification threshold, Logistic Regression flagged only 63 of 61,502 validation applications.

Among those flagged, approximately 52.4% had recorded repayment difficulties.

However, recall was just 0.66%, meaning approximately 99.34% of positive cases were not identified.

This result illustrates that a model can achieve useful ranking performance while identifying very few positive cases at a high decision threshold.

### 5.2 Lower Threshold: 0.10

Reducing the threshold to 0.10 increased recall to 60.1%.

The model flagged 16,566 applicants, of whom 2,983 had recorded repayment difficulties and 13,583 did not.

Compared with the 0.50 threshold, this substantially improved positive-case identification but increased the number of false-positive flags and the review workload.

At this threshold, precision was 18.0%, meaning approximately 18 of every 100 flagged applications belonged to the positive class.

### 5.3 High-Recall Threshold: 0.05

At the 0.05 threshold, recall reached 84.4%, with only 773 positive cases missed.

However, the model flagged 35,068 applicants—approximately 57% of the validation population.

Of those flagged, 30,876 were false positives.

This threshold could be relevant for a hypothetical screening process prioritizing the identification of most positive cases, but it would introduce substantial operational workload and potential costs.

### 5.4 Risk Decision Interpretation

The analysis demonstrates a fundamental trade-off between positive-case detection and the number of applicants incorrectly flagged.

Lower thresholds increase recall but also increase false positives. Higher thresholds improve the concentration of positive cases among flagged applicants while missing more actual positive cases.

No single threshold can be considered optimal without defining the intended application, operational capacity, consequences of false positives, and costs of missed cases.

The thresholds analyzed here are exploratory and should not be interpreted as recommended real-world lending cutoffs.

## 6. Key Analytical Conclusions

### Predictive Value of Financial Features

Logistic Regression substantially outperformed the dummy baseline across ROC-AUC, Average Precision, and Brier Score.

This suggests that the selected financial and historical credit features contain predictive information about the dataset's repayment-difficulty outcome.

### Impact of Class Imbalance

The 8.07% positive-class prevalence makes classification accuracy and default-threshold metrics insufficient for evaluating the model.

ROC-AUC and Average Precision provided more informative assessments of ranking performance.

### Importance of Threshold Optimization

Threshold analysis demonstrated that the 0.50 cutoff identifies very few positive cases despite relatively high precision.

Lower thresholds substantially increase recall while introducing additional false positives, highlighting the importance of aligning model evaluation with the intended decision-making objective.

### Need for Further Model Evaluation

Although Logistic Regression provides a useful baseline, additional model comparisons are needed to determine whether nonlinear methods can improve risk discrimination.

Probability calibration, cross-validation stability, and model interpretability also require further investigation.

## 7. Limitations

The analysis uses a retrospective financial dataset and random stratified sampling rather than out-of-time validation.

Although preprocessing was fitted on training data, feature provenance and point-in-time availability require additional review before any operational interpretation.

The model's performance has only been assessed on the validation set in this phase; held-out test performance remains unknown.

Results do not establish causal relationships between borrower characteristics and repayment difficulties.

Furthermore, the implications of using credit risk predictions in actual lending decisions would require careful consideration of fairness, regulatory requirements, and consequences for affected applicants.

## 8. Next Steps — Day 6

The next phase will focus on advanced predictive modeling using gradient boosting.

Planned tasks include:

- Training a LightGBM classifier using the same development data.
- Comparing LightGBM against Logistic Regression using consistent validation metrics.
- Investigating nonlinear financial relationships and feature interactions.
- Evaluating hyperparameter choices and potential overfitting.
- Assessing whether the advanced model improves ranking performance, positive-case identification, and probability estimates.

**Tools:** Python, pandas, NumPy, scikit-learn, Logistic Regression, DuckDB, matplotlib.

**Project:** Home Credit Default Risk — Baseline Credit Risk Prediction & Classification Threshold Analysis.