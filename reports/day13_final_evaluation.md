# Day 13 — Final Held-Out Model Evaluation

## 1. Executive Summary

This phase evaluated the previously developed LightGBM credit risk model and Logistic Regression baseline on the original held-out test partition, consisting of **61,503 applications** with **4,965 recorded positive outcomes**. The test data had not been used for training, model selection, early stopping, or validation-based threshold analysis.

**LightGBM retained its advantage on all three primary test metrics:** ROC-AUC **0.7487** versus **0.7382** for Logistic Regression; Average Precision **0.2329** versus **0.2179**; and Brier Score **0.06838** versus **0.06901**. LightGBM's Average Precision was approximately **6.9% higher** relative to Logistic Regression.

LightGBM test performance was modestly below validation performance, but the decline was small. Paired bootstrap intervals for model differences excluded zero in LightGBM's favor for all three metrics. The previously selected **0.06 threshold** captured **77.66%** of test positives, while a strict **20% screening capacity** captured **50.03%**.

The analysis is an assessment of predictive performance on historical data, not a validated lending policy. All cost results below use hypothetical units.

## 2. Dataset, Protocol, and Model Provenance

| Partition | Applications | Purpose |
|---|---:|---|
| Training | 184,506 | Model fitting |
| Validation | 61,502 | Model development, early stopping, exploratory screening choices |
| Final test | 61,503 | Held-out performance evaluation |

The original stratified 60/20/20 partition and applicant-level feature selection were preserved. The saved Day 6 LightGBM estimator and its training-fitted preprocessing pipeline were reused without refitting. Logistic Regression was reproduced on the original training partition with the previously established configuration. Model evaluation used the same test observations for both classifiers.

The candidate screening policies were frozen before examining test labels: probability threshold **0.06**, and strict top-**20%** scoring capacity using integer-floor rounding. The test set was not used to choose a new model, feature set, threshold, or screening capacity.

## 3. Final Held-Out Model Performance

| Metric | Logistic Regression | LightGBM | Difference (LightGBM − Logistic) |
|---|---:|---:|---:|
| ROC-AUC | 0.738241 | **0.748732** | +0.010491 |
| Average Precision | 0.217922 | **0.232914** | +0.014992 |
| Brier Score | 0.069009 | **0.068375** | −0.000634 |

The LightGBM classifier demonstrated stronger discrimination and average precision, with a modestly lower mean squared probability error. The relative Average Precision gain was approximately **6.9%**. Since the outcome prevalence is approximately 8.07%, Average Precision is particularly informative about ranking under substantial class imbalance.

### Validation-to-Test Generalization

| Model | Metric | Validation | Test | Test − Validation |
|---|---|---:|---:|---:|
| Logistic Regression | ROC-AUC | 0.744099 | 0.738241 | −0.005858 |
| Logistic Regression | Average Precision | 0.220843 | 0.217922 | −0.002921 |
| Logistic Regression | Brier Score | 0.068793 | 0.069009 | +0.000215 |
| LightGBM | ROC-AUC | 0.754074 | 0.748732 | −0.005342 |
| LightGBM | Average Precision | 0.237255 | 0.232914 | −0.004340 |
| LightGBM | Brier Score | 0.068063 | 0.068375 | +0.000312 |

Both models performed slightly worse on the test partition than on the validation partition. The decreases were relatively small, supporting reasonable generalization within this historical dataset. The result is not evidence of stability under temporal or geographic distribution shift.

## 4. Bootstrap Uncertainty

### LightGBM 95% Bootstrap Intervals

| Metric | Bootstrap mean | Lower bound | Upper bound |
|---|---:|---:|---:|
| ROC-AUC | 0.748911 | 0.742110 | 0.754913 |
| Average Precision | 0.233435 | 0.223286 | 0.244105 |
| Brier Score | 0.068347 | 0.066733 | 0.070050 |

### Paired Model Comparison

| Metric (LightGBM − Logistic) | Bootstrap mean difference | 95% interval |
|---|---:|---|
| ROC-AUC | +0.010561 | +0.007817 to +0.013266 |
| Average Precision | +0.015027 | +0.010327 to +0.020189 |
| Brier Score | −0.000638 | −0.000826 to −0.000449 |

The intervals for all paired differences excluded zero in LightGBM's favor. The paired design preserves the fact that both models were evaluated on the same observations. These approximate intervals describe test-sample variation, conditional on the fitted models; they do not incorporate model-training uncertainty or time-dependent drift.

## 5. Frozen Probability Threshold: 0.06

The threshold was selected during Day 10 using validation outcomes and the following **illustrative** objective:

**Modeled Cost = 25 × Reviewed Applications + 500 × Unflagged Positive Cases**.

| Metric | Validation | Held-out test |
|---|---:|---:|
| Applications reviewed | 27,951 | **27,833** |
| Review rate | 45.45% | **45.25%** |
| True positives | 3,895 | **3,856** |
| False positives | 24,056 | **23,977** |
| False negatives | 1,070 | **1,109** |
| True negatives | 32,481 | **32,561** |
| Precision | 13.94% | **13.85%** |
| Recall | 78.45% | **77.66%** |
| Modeled cost | 1,233,775 | **1,250,325** |

Test modeled cost was **27,833 × 25 + 1,109 × 500 = 1,250,325 hypothetical units**.

Recall declined by approximately **0.79 percentage points** compared with validation. The threshold still captured more than three-quarters of positives, but required review of approximately 45% of applications. It should not be treated as a real-world optimal lending threshold; costs and review effectiveness were not empirically estimated.

## 6. Frozen Fixed-Capacity Screening: Top 20%

A strict 20% capacity limit permits **12,300 applications** in the 61,503-row test partition, using floor rounding. The corrected validation run also selected **12,300 applications**.

| Metric | Validation | Held-out test |
|---|---:|---:|
| Applications reviewed | 12,300 | **12,300** |
| Review rate | 20.00% | **20.00%** |
| True positives | 2,572 | **2,484** |
| False positives | 9,728 | **9,816** |
| False negatives | 2,393 | **2,481** |
| True negatives | 46,809 | **46,722** |
| Precision | 20.91% | **20.20%** |
| Recall | 51.80% | **50.03%** |
| Test cumulative lift | — | **2.50×** |
| Modeled cost | 1,504,000 | **1,548,000** |

The test screening captured **2,484 of 4,965 positives**, with **2.50× lift** relative to the test-set prevalence. Recall was approximately **1.77 percentage points** lower than validation. The modeled test cost was **12,300 × 25 + 2,481 × 500 = 1,548,000 hypothetical units**.

The test-set top-20% policy was not reoptimized after these results were observed. Its capacity and ranking rule were predetermined.

## 7. Final Test Risk Deciles

| Predicted-risk decile | Applications | Positive cases | Observed difficulty | Mean predicted risk | Lift |
|---:|---:|---:|---:|---:|---:|
| 1 | 6,151 | 81 | 1.32% | 1.51% | 0.16× |
| 2 | 6,150 | 135 | 2.20% | 2.32% | 0.27× |
| 3 | 6,150 | 184 | 2.99% | 3.04% | 0.37× |
| 4 | 6,150 | 216 | 3.51% | 3.83% | 0.44× |
| 5 | 6,151 | 314 | 5.10% | 4.80% | 0.63× |
| 6 | 6,150 | 377 | 6.13% | 6.05% | 0.76× |
| 7 | 6,150 | 506 | 8.23% | 7.73% | 1.02× |
| 8 | 6,150 | 667 | 10.85% | 10.22% | 1.34× |
| 9 | 6,150 | 886 | 14.41% | 14.43% | 1.78× |
| 10 | 6,151 | 1,599 | **26.00%** | **26.97%** | **3.22×** |

Observed difficulty increased monotonically across all ten score deciles, from **1.32%** in the lowest to **26.00%** in the highest. The highest decile's observed positive rate was approximately **19.7 times** the lowest decile's rate, and lift in the highest decile was **3.22×**.

The top two deciles contained **2,485 positive cases**, representing approximately **50.05%** of all positives. This is one case higher than the strict top-20% policy's 2,484 positives because two complete deciles contain 12,301 applications, whereas a strict 20% cap permits only 12,300.

Mean predicted probabilities were generally close to observed positive rates across deciles. In the highest decile, the model predicted 26.97% on average versus an observed 26.00%, an overprediction of approximately **0.97 percentage points**. This is encouraging decile-level calibration evidence, not a guarantee of reliability for individual applications.

## 8. Final Assessment

LightGBM **retained a measurable test-set advantage** over Logistic Regression in ROC-AUC, Average Precision, and Brier Score. Small validation-to-test performance declines suggest reasonable generalization within the original historical sample, and paired bootstrap comparisons favor LightGBM on all three metrics.

The model also produced meaningful risk differentiation: higher predicted-risk deciles had substantially higher observed positive rates. The frozen screening analyses demonstrate predictable workload-versus-capture tradeoffs without using test outcomes to optimize new thresholds.

These findings support the project as an end-to-end analytical demonstration. They do **not** establish readiness for production credit decisions.

## 9. Limitations

- Historical, randomly split data do not measure future temporal stability or changes in economic conditions.
- LightGBM early stopping and policy selection used validation data; the test set was reserved for final assessment.
- Feature provenance, availability at application time, and potential data leakage require further independent verification.
- Predictive variables may encode sensitive attributes or proxies; fair lending and subgroup impact would require rigorous assessment.
- SHAP explanations describe model attribution, not causal determinants of repayment difficulty.
- The review-cost assumptions are hypothetical, and selecting a positive case does not establish that any actual credit loss would be prevented.
- The target reflects the dataset's recorded payment-difficulty definition, not a general guarantee of future default.
- Bootstrap uncertainty estimates do not capture all sources of model or population uncertainty.

## 10. Day 14 — Portfolio Finalization

Update README and dashboard tables with clearly labeled **held-out test** metrics while preserving earlier **validation** results for the corresponding historical experiments. Audit all CSV values, charts, environment files, and deployment instructions. Run the dashboard against committed aggregate data, inspect GitHub rendering, and prepare a concise technical project summary and resume bullets.

**Tools:** Python, LightGBM, scikit-learn, DuckDB, pandas, NumPy, matplotlib, bootstrap resampling.
