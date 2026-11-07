# Day 6 — LightGBM Credit Risk Modeling & Model Comparison

## 1. Executive Summary

This phase evaluated whether gradient-boosted decision trees improve credit risk prediction compared with the Logistic Regression baseline developed during Day 5.

LightGBM was trained using the same feature-engineered dataset, preprocessing approach, and training-validation partitions as Logistic Regression. Hyperparameter regularization and validation-based early stopping were applied to limit model complexity.

**Key findings:**

- LightGBM achieved a validation ROC-AUC of **0.7541**, compared with 0.7441 for Logistic Regression.
- Average Precision improved from **0.2208 to 0.2373**, representing approximately a 7.5% relative improvement.
- Brier Score decreased from **0.0688 to 0.0681**, indicating slightly improved probability prediction performance.
- At a fixed review capacity of 10% of applications, LightGBM achieved **27.13% Precision@K and 33.62% Recall@K**, outperforming Logistic Regression.
- Application-level financial variables, external-source scores, employment history, and engineered bureau credit features were among LightGBM's most frequently selected splitting variables.

Overall, LightGBM demonstrated better predictive discrimination and slightly stronger probability accuracy, while fixed-capacity screening analysis showed its potential advantages for prioritizing higher-risk applications.

## 2. Model Development

LightGBM was trained using 184,506 applications, with 61,502 applications reserved for validation and 61,503 held out for final testing.

The model used gradient-boosted decision trees with controlled learning rate, tree complexity, feature subsampling, observation subsampling, and L2 regularization.

Early stopping was configured to monitor validation ROC-AUC, stopping after 50 rounds without improvement.

The best model iteration was **524**, achieving a validation ROC-AUC of approximately **0.754074**.

## 3. Predictive Performance Comparison

| Metric | Logistic Regression | LightGBM |
|---|---:|---:|
| ROC-AUC | 0.7441 | 0.7541 |
| Average Precision | 0.2208 | 0.2373 |
| Brier Score | 0.0688 | 0.0681 |
| Precision @ 0.10 | 0.1801 | 0.1877 |
| Recall @ 0.10 | 0.6008 | 0.5954 |
| Applicants Flagged @ 0.10 | 16,566 | 15,745 |

### ROC-AUC Analysis

LightGBM improved ROC-AUC by 0.0100, increasing the model's ability to rank applicants with recorded payment difficulties above those without.

The ROC curves show that LightGBM generally achieves slightly better discrimination, although the difference is relatively small.

### Precision-Recall Analysis

LightGBM achieved an Average Precision of 0.2373, compared with 0.2208 for Logistic Regression.

This represents an absolute improvement of 0.0165 and a relative improvement of approximately 7.5%.

The precision-recall curve demonstrates that LightGBM generally maintains higher precision over portions of the recall range, particularly when prioritizing smaller groups of higher-scoring applications.

These improvements are relevant given the dataset's positive-class prevalence of approximately 8.07%.

### Probability Performance

LightGBM reduced Brier Score from 0.0688 to 0.0681, suggesting a modest improvement in the accuracy of predicted probabilities.

Calibration curves for both models were close to the ideal diagonal across the displayed probability range.

Further calibration analysis is necessary before concluding that the predicted probabilities are sufficiently reliable for operational decision-making.

## 4. Classification Threshold Analysis

At a probability threshold of 0.10:

| Metric | Logistic Regression | LightGBM |
|---|---:|---:|
| Applications Flagged | 16,566 | 15,745 |
| Precision | 18.0% | 18.8% |
| Recall | 60.1% | 59.5% |
| False Positives | 13,583 | 12,789 |
| False Negatives | 1,982 | 2,009 |

LightGBM flagged 821 fewer applications and produced 794 fewer false positives at this threshold.

However, it also missed 27 additional positive cases, resulting in slightly lower recall.

This demonstrates that improved ranking performance does not guarantee improvement in every metric at a fixed probability threshold.

## 5. Fixed-Capacity Screening Analysis

To compare the models under identical screening constraints, the highest-risk 10% of validation applications were selected from each model's predicted probability rankings.

| Metric | Logistic Regression | LightGBM |
|---|---:|---:|
| Applications Reviewed | 6,151 | 6,151 |
| Precision@K | 25.78% | 27.13% |
| Recall@K | 31.94% | 33.62% |

LightGBM improved Precision@K by **1.35 percentage points** and Recall@K by **1.68 percentage points**.

At the same screening capacity, this corresponds to approximately 83 additional positive cases identified.

These results indicate that LightGBM provides a more effective ranking of applicants for a hypothetical limited-capacity review process.

Actual operational benefits would depend on review costs, model stability, fairness, and the consequences of incorrect classifications.

## 6. Feature Importance Analysis

LightGBM's most frequently used features included:

- External-source scores (`EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3`)
- Requested credit amount (`AMT_CREDIT`)
- Loan annuity (`AMT_ANNUITY`)
- Employment duration (`employment_years`)
- Historical credit age (`bureau_avg_days_since_credit`)
- Total bureau credit exposure (`bureau_total_credit`)
- Credit-to-income and annuity-to-income ratios
- Historical credit account and debt indicators

These results demonstrate that the model uses information from both original application variables and engineered historical bureau features.

The prominence of bureau-derived variables supports investigating whether historical credit information contributes additional predictive value.

However, split-based feature importance does not establish independent predictive contribution, causal relationships, or the direction of risk effects.

Further analysis using permutation importance, feature ablation, and SHAP explanations is recommended.

## 7. Key Conclusions

**Improved predictive discrimination:** LightGBM outperformed Logistic Regression in ROC-AUC and Average Precision.

**Improved fixed-capacity ranking:** LightGBM identified more positive cases when both models reviewed the same 10% of applicants.

**Threshold sensitivity:** LightGBM did not outperform Logistic Regression on recall at every identical probability threshold, emphasizing the importance of comparing models under consistent operational constraints.

**Value of feature engineering:** Application-level financial characteristics and historical credit features appeared prominently in model split importance, although their incremental predictive benefit remains unverified.

**Probability reliability:** LightGBM showed a modest improvement in Brier Score, but additional calibration testing is warranted.

## 8. Limitations

The results were obtained on the validation set, which was also used for early stopping. Consequently, validation performance may be somewhat optimistic.

The held-out test set has not been evaluated.

The dataset represents historical payment-difficulty outcomes, and descriptive or predictive associations do not establish causality.

Potential issues concerning data leakage, point-in-time feature availability, sensitive or proxy variables, and operational fairness require further investigation.

## 9. Next Steps — Day 7

The next phase will investigate model robustness and generalization.

Planned work includes:

- Cross-validation to estimate performance stability.
- Investigating differences between training and validation performance.
- Feature ablation to measure the incremental value of bureau history.
- Reviewing feature availability and potential leakage.
- Comparing model performance across selected borrower segments.
- Selecting a modeling strategy for subsequent explainability and decision analysis.

**Tools:** Python, LightGBM, scikit-learn, DuckDB, pandas, NumPy, matplotlib.

**Project:** Home Credit Default Risk — Advanced Predictive Modeling & Risk Analysis.