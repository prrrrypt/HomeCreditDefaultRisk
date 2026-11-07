# Day 8 — Explainable AI: Interpreting LightGBM Credit Risk Predictions

## 1. Executive Summary

This phase applied SHAP (SHapley Additive exPlanations) to explain the LightGBM credit risk model developed during Day 6.

The analysis examined global feature importance, feature-response relationships, individual prediction explanations, and historical credit contributions across predicted-risk deciles.

**Key findings:**

- External-source scores were the strongest individual predictors, with `EXT_SOURCE_2` and `EXT_SOURCE_3` achieving mean absolute SHAP values of 0.3414 and 0.3091, respectively.
- Employment duration, loan annuity, credit amount, and engineered bureau credit features also contributed meaningfully to model predictions.
- Lower `EXT_SOURCE_2` values generally increased predicted repayment-difficulty risk, while longer employment histories generally reduced predicted risk.
- Historical credit features produced negative mean net SHAP contributions for the six lowest predicted-risk deciles and positive contributions for the four highest deciles.
- Individual explanations demonstrated how different financial characteristics could reinforce or offset one another within the same prediction.

These findings complement Day 7's feature ablation results, which showed that adding bureau-derived features improved cross-validation Average Precision by approximately 5.23% relative to an application-only model.

## 2. Methodology

The previously trained LightGBM classifier was loaded together with its fitted preprocessing pipeline.

A reproducible sample of 1,000 observations was drawn from the validation dataset. The original held-out test set remained unused.

The original 27 input variables expanded to 61 transformed model features after numerical preprocessing, missingness indicators, and categorical one-hot encoding.

Tree SHAP was used to explain the classifier's raw log-odds output.

The SHAP expected value was −2.7860 log-odds, corresponding to approximately 5.81% after sigmoid transformation.

An additivity check verified that the baseline plus feature SHAP values reconstructed model outputs, with a maximum absolute numerical error of approximately 1.29 × 10⁻¹⁴.

All feature contributions are reported in log-odds units rather than probability percentage points.

## 3. Global Feature Importance

The ten most influential transformed features by mean absolute SHAP value were:

| Rank | Feature | Mean Absolute SHAP |
|---:|---|---:|
| 1 | EXT_SOURCE_2 | 0.3414 |
| 2 | EXT_SOURCE_3 | 0.3091 |
| 3 | EXT_SOURCE_1 | 0.1624 |
| 4 | Employment years | 0.1231 |
| 5 | Loan annuity | 0.1083 |
| 6 | Credit amount | 0.0999 |
| 7 | Bureau debt-to-credit ratio | 0.0744 |
| 8 | Higher education indicator | 0.0671 |
| 9 | Working income-type indicator | 0.0632 |
| 10 | Secondary education indicator | 0.0542 |

### Interpretation

External-source scores accounted for the largest individual contributions to model predictions.

Among financial characteristics, employment duration, loan annuity, and requested credit amount had substantial influence.

Engineered bureau variables also appeared in the importance ranking, including debt-to-credit ratio, active account counts, total historical credit, and average credit-history age.

These findings demonstrate that the model combines external-source indicators with applicant-level financial characteristics and historical credit information.

Compared with Day 6 split-based feature importance, SHAP provides a different view of importance: the magnitude of contributions to predictions rather than the number of times a variable appears in tree splits.

## 4. Feature Relationships

### 4.1 External-Source Scores

`EXT_SOURCE_2` displayed a strong, nearly monotonic inverse relationship with its SHAP contribution.

Lower score values typically increased the raw predicted risk score, while higher values reduced it.

The beeswarm plot showed a similar overall pattern for `EXT_SOURCE_3` and `EXT_SOURCE_1`.

These variables were the dominant individual features in the global explanation analysis.

### 4.2 Credit Amount

Requested credit amount displayed a nonlinear relationship with SHAP values.

Smaller credit amounts frequently contributed negatively to model output, intermediate amounts were more often associated with positive contributions, and larger amounts frequently had negative contributions.

This pattern should be interpreted as model behavior conditional on the available predictors, not evidence that increasing credit amounts reduces actual repayment risk.

### 4.3 Employment Duration

Employment duration showed a broadly decreasing relationship with the model's raw risk score.

Shorter employment histories generally had positive SHAP contributions, while longer histories tended to have negative contributions.

This supports the observation that the model treats employment stability as an informative predictive characteristic.

### 4.4 Historical Credit Age

Average days since historical bureau credit showed a weaker, nonlinear relationship.

Intermediate credit-history ages frequently produced negative contributions, although considerable variation remained.

This indicates that historical account age provides information whose effect depends on the wider financial context.

## 5. Individual Prediction Explanations

Two observations were selected from the 1,000-row validation sample: the highest-scoring and lowest-scoring applications.

### 5.1 Highest-Scoring Example

**Predicted repayment-difficulty probability: 60.16%**

The model's raw prediction was approximately +0.412 log-odds.

The largest upward contributions included a low `EXT_SOURCE_3` value, active bureau credit accounts, a low `EXT_SOURCE_2` value, bureau debt-to-credit ratio, loan annuity, and employment characteristics.

Not every feature contributed in the same direction. For example, `bureau_total_debt` contributed approximately −0.25 log-odds, partially offsetting upward contributions from other features.

This demonstrates how different historical credit measures can have distinct effects within the same application.

### 5.2 Lowest-Scoring Example

**Predicted repayment-difficulty probability: 0.66%**

The model's raw prediction was approximately −5.019 log-odds.

The main downward contributions included `EXT_SOURCE_2`, `EXT_SOURCE_1`, employment duration, credit amount, education and income-type indicators, and selected historical credit characteristics.

The contrast between the two examples demonstrates that LightGBM combines multiple financial attributes rather than relying on a single variable.

These cases were selected because they represented prediction extremes in the sample. They are not representative of typical borrowers.

## 6. Historical Credit Contributions by Predicted-Risk Decile

Historical bureau SHAP contributions were aggregated across the engineered bureau feature group and compared across ten equal-sized predicted-risk segments.

| Risk Decile | Mean Predicted Probability | Mean Net Bureau SHAP | Mean Total Absolute Bureau SHAP |
|---:|---:|---:|---:|
| 1 | 0.0146 | −0.1581 | 0.3080 |
| 2 | 0.0216 | −0.1277 | 0.2944 |
| 3 | 0.0289 | −0.0931 | 0.2845 |
| 4 | 0.0370 | −0.0363 | 0.2780 |
| 5 | 0.0455 | −0.0385 | 0.3145 |
| 6 | 0.0579 | −0.0213 | 0.2838 |
| 7 | 0.0741 | +0.0401 | 0.3085 |
| 8 | 0.0974 | +0.0226 | 0.3199 |
| 9 | 0.1309 | +0.0384 | 0.3189 |
| 10 | 0.2621 | +0.1757 | 0.3990 |

### Interpretation

The first six deciles showed negative mean net bureau SHAP contributions, indicating that historical credit features generally reduced raw model scores for these groups relative to the SHAP baseline.

The four highest predicted-risk deciles showed positive mean net contributions.

The tenth decile had the largest positive net contribution (+0.1757 log-odds) and the largest total absolute bureau attribution (0.3990).

This suggests that the model uses historical credit information more strongly in some of its highest-scoring predictions.

However, the groups are defined using the model's own predicted probabilities. The pattern is descriptive and does not independently demonstrate model accuracy or causality.

## 7. Key Conclusions

**External-source score dependence:** The strongest individual contributions came from the three external-source indicators, suggesting that the model relies substantially on these existing predictive signals.

**Nonlinear financial relationships:** Loan amounts, employment history, and bureau account age exhibited different and sometimes nonlinear contribution patterns.

**Historical credit relevance:** Engineered bureau features contributed to both global and individual explanations and displayed systematic differences across predicted-risk deciles.

**Consistency with feature ablation:** Day 7 established that including bureau features improved cross-validation Average Precision by approximately 5.23%. Day 8 provides complementary insight into how those variables affect the model's predictions.

**Interpretability:** SHAP enabled the decomposition of individual predictions into a baseline and feature-level contributions, helping make the LightGBM model more transparent.

## 8. Limitations

SHAP values explain predictive model behavior, not the causal effects of financial variables.

The analysis was based on a 1,000-observation validation sample rather than the full applicant population.

Feature attributions depend on the fitted model, transformations, correlated inputs, and SHAP feature-dependence assumptions.

Numerical features were transformed before modeling, so SHAP waterfall values display scaled feature inputs rather than original financial units.

The model's external-source variables require further investigation concerning data provenance, availability at application time, transparency, and potential proxy effects.

Individual SHAP explanations are not sufficient evidence for making or justifying real lending decisions.

The final held-out test set remains reserved for later evaluation.

## 9. Next Steps

Day 9 will investigate risk segmentation and score distributions, including:

- Grouping validation applications into predicted-risk deciles.
- Comparing observed repayment-difficulty rates across score groups.
- Evaluating the concentration of positive cases in the highest-risk segments.
- Investigating model behavior across selected financial characteristics.
- Preparing interpretable results for a future dashboard.

**Tools:** Python, LightGBM, SHAP, scikit-learn, pandas, NumPy, matplotlib, DuckDB.