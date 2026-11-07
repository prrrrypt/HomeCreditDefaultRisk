# Day 9 — Credit Risk Segmentation & Portfolio Analysis

## 1. Executive Summary

This phase translated LightGBM predicted repayment-difficulty probabilities into portfolio-level risk segments and evaluated their relationship with actual historical outcomes.

The analysis examined predicted-risk deciles, cumulative capture, lift, probability calibration, and model performance across financial subgroups.

**Key findings:**

- Observed repayment-difficulty rates increased monotonically across all ten predicted-risk deciles, from **1.58% in the lowest decile to 27.13% in the highest**.
- The highest-risk decile achieved a lift of **3.36×** relative to the overall positive-class prevalence of approximately 8.07%.
- The highest-scoring 20% of validation applications contained **51.80% of all positive cases**.
- Predicted probabilities closely matched observed difficulty rates at the decile level, particularly in the highest-risk group.
- Model ROC-AUC across income quintiles ranged from 0.7369 to 0.7645.
- Higher annuity-to-income burdens were generally associated with greater observed payment difficulty.
- Model discrimination appeared weaker for applicants without matched credit bureau history, warranting further investigation.

These findings demonstrate that LightGBM produces meaningful validation-set risk rankings that can support descriptive portfolio analysis and hypothetical screening-capacity evaluation.

## 2. Dataset and Methodology

The previously trained LightGBM classifier was applied to the original validation partition of **61,502 applications**, including **4,965 positive cases**.

No model retraining was performed. The held-out test set remained untouched.

Applications were ranked by predicted repayment-difficulty probability and divided into ten approximately equally sized groups.

The analysis calculated observed positive rates, predicted probabilities, lift, cumulative capture, and performance metrics across income, annuity-burden, and credit bureau history groups.

## 3. Predicted-Risk Decile Analysis

| Decile | Applicants | Positive Cases | Observed Rate | Mean Predicted Risk | Lift |
|---:|---:|---:|---:|---:|---:|
| 1 | 6,151 | 97 | 1.58% | 1.51% | 0.20× |
| 2 | 6,150 | 117 | 1.90% | 2.32% | 0.24× |
| 3 | 6,150 | 181 | 2.94% | 3.03% | 0.36× |
| 4 | 6,150 | 231 | 3.76% | 3.83% | 0.47× |
| 5 | 6,150 | 302 | 4.91% | 4.82% | 0.61× |
| 6 | 6,150 | 340 | 5.53% | 6.08% | 0.68× |
| 7 | 6,150 | 482 | 7.84% | 7.79% | 0.97× |
| 8 | 6,150 | 643 | 10.46% | 10.24% | 1.30× |
| 9 | 6,150 | 903 | 14.68% | 14.55% | 1.82× |
| 10 | 6,151 | 1,669 | 27.13% | 26.99% | 3.36× |

### Interpretation

Observed repayment-difficulty rates increased consistently from the lowest to the highest decile.

The highest-decile observed rate was approximately 17.2 times that of the lowest decile.

This indicates that the model effectively distinguishes applicants with different levels of historically observed repayment difficulty on the validation dataset.

The highest-risk decile had an observed rate of 27.13%, compared with an overall positive-class prevalence of approximately 8.07%, yielding a lift of 3.36×.

### Statistical Uncertainty

Wilson 95% confidence intervals were calculated for each decile's observed positive rate.

The lowest-decile interval was 1.29%–1.92%, whereas the highest-decile interval was 26.04%–28.26%.

The substantial separation supports the finding that the model ranks applications into meaningfully differentiated risk groups.

These intervals do not incorporate model-selection uncertainty or future population changes.

## 4. Cumulative Capture and Lift

| Review Capacity | Applicants Reviewed | Positive Cases Captured | Recall | Cumulative Lift |
|---|---:|---:|---:|---:|
| Top 10% | 6,151 | 1,669 | 33.62% | 3.36× |
| Top 20% | 12,301 | 2,572 | 51.80% | 2.59× |
| Top 30% | 18,451 | 3,215 | 64.75% | 2.16× |
| Top 40% | 24,601 | 3,697 | 74.46% | 1.86× |
| Top 50% | 30,751 | 4,037 | 81.31% | 1.63× |

### Interpretation

The highest-scoring 10% of applicants contained approximately one-third of all positive cases, while the highest-scoring 20% contained more than half.

At a 30% review capacity, the model captured 64.75% of positive cases, corresponding to a cumulative lift of approximately 2.16× relative to random selection.

The cumulative gains curve remained above the random-selection benchmark across the evaluated screening capacities.

These findings demonstrate the model's ability to concentrate positive historical outcomes among higher-scoring applications.

## 5. Probability Calibration by Risk Decile

The decile-level comparison showed close agreement between average predicted probabilities and observed positive rates.

In the highest-risk decile, the mean predicted probability was 26.99%, compared with an observed rate of 27.13%.

The sixth decile showed a larger difference, with 6.08% predicted versus 5.53% observed.

Overall, the analysis provides encouraging evidence of calibration across score groups, while further independent testing remains necessary.

## 6. Financial Segmentation

### 6.1 Income Quintiles

| Income Quintile | Observed Difficulty | ROC-AUC |
|---:|---:|---:|
| 1 | 8.18% | 0.7522 |
| 2 | 8.79% | 0.7568 |
| 3 | 8.55% | 0.7369 |
| 4 | 8.44% | 0.7645 |
| 5 | 6.41% | 0.7520 |

The highest-income quintile exhibited the lowest observed difficulty rate, while the second income quintile had the highest.

The relationship was non-monotonic, consistent with the earlier borrower-level exploratory analysis.

Model discrimination ranged from 0.7369 to 0.7645, indicating moderate variation across income groups.

The third quintile had the lowest ROC-AUC, suggesting an area for further performance investigation.

### 6.2 Annuity-to-Income Burden

| Burden Quintile | Observed Difficulty | ROC-AUC |
|---:|---:|---:|
| 1 | 6.71% | 0.7456 |
| 2 | 7.80% | 0.7646 |
| 3 | 8.44% | 0.7455 |
| 4 | 8.75% | 0.7631 |
| 5 | 8.67% | 0.7464 |

Observed repayment difficulty generally increased with annuity burden.

The fourth quintile recorded the highest observed positive rate at 8.75%, compared with 6.71% in the lowest burden quintile.

The highest quintile had a slightly lower rate of 8.67%, indicating that the relationship is not perfectly monotonic.

Two validation observations lacked an annuity-burden quintile assignment. Their subgroup contained no positive outcomes, so discrimination metrics could not be calculated.

### 6.3 Historical Bureau Availability

The subgroup ROC-AUC visualization indicated stronger model discrimination among applicants with matched historical bureau records than among applicants without such records.

Approximate ROC-AUC values from the visualization were 0.76 and 0.71, respectively.

These values require confirmation from the exact subgroup results table before being treated as final numerical findings.

This difference warrants further investigation into missing credit history, feature availability, and variation in model performance across populations.

The absence of matched bureau records should not be interpreted as evidence of unfavorable creditworthiness.

## 7. Business Interpretation

The analysis demonstrates how predicted scores can be translated into interpretable portfolio-level indicators.

Risk deciles identify meaningful differences in historically observed repayment difficulty. Cumulative capture and lift quantify how effectively a model concentrates positive cases within a limited review population.

Subgroup analysis highlights where ranking performance and probability calibration may differ across financial characteristics.

These findings can support model evaluation and analytical reporting, but they do not establish that the model is suitable for automated lending decisions.

## 8. Limitations

The analysis uses the validation partition previously involved in model development.

Risk deciles represent relative rankings within this dataset, not universally applicable risk categories.

The subgroup analysis is descriptive and does not establish causal relationships.

The dataset's historical outcomes, sampling structure, and feature availability may differ from those of future applications.

Fairness, proxy discrimination, regulatory compliance, population stability, and cost-sensitive evaluation require further investigation.

The held-out test set remains reserved for final model assessment.

## 9. Next Steps — Day 10

The next phase will evaluate alternative screening thresholds using confusion matrices, precision-recall tradeoffs, and hypothetical error costs.

The analysis will compare probability thresholds with fixed-capacity review strategies and identify how operational assumptions change preferred screening decisions.

The resulting metrics and aggregate tables will support development of an interactive risk analytics dashboard.

**Tools:** Python, pandas, LightGBM, scikit-learn, DuckDB, matplotlib, statsmodels.