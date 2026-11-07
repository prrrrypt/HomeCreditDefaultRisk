# Day 3 — Borrower Risk Analysis Findings

## 1. Executive Summary

This analysis examines the relationship between borrower financial characteristics and repayment difficulties using 307,511 loan applications from the Home Credit Default Risk dataset.

Using SQL and DuckDB, applicants were segmented by credit-to-income ratio, income level, annuity-to-income ratio, and employment duration. Window functions, Common Table Expressions (CTEs), and aggregate statistics were used to calculate observed payment-difficulty rates across borrower groups.

**Key findings:**

- Employment duration demonstrated the clearest relationship with repayment difficulties, with shorter employment histories associated with higher observed difficulty rates.
- Credit-to-income ratios displayed a non-linear relationship with payment difficulties, suggesting that higher requested credit relative to income does not automatically correspond to higher observed risk.
- Higher-income applicants generally experienced lower difficulty rates at the upper end of the income distribution.
- Annuity-to-income ratios showed a moderate association with repayment difficulties, although the relationship was not strictly increasing.

These findings establish a foundation for financial feature engineering and predictive risk modeling.

## 2. Credit-to-Income Ratio Analysis

**Objective:** Investigate whether higher requested credit relative to annual income is associated with increased repayment difficulties.

Applicants were divided into five approximately equal-sized groups based on their credit-to-income ratios.

| Quintile | Avg. Credit/Income | Difficulty Rate |
|---|---:|---:|
| 1 | 1.27 | 7.33% |
| 2 | 2.28 | 8.57% |
| 3 | 3.28 | 8.93% |
| 4 | 4.75 | 8.28% |
| 5 | 8.21 | 7.25% |

### Findings

The results reveal a **non-linear relationship** between credit-to-income ratio and observed repayment difficulties.

The difficulty rate initially increases from 7.33% in the lowest quintile to a peak of 8.93% in the third quintile, representing an increase of 1.60 percentage points. However, the rate subsequently decreases to 7.25% in the highest quintile.

This pattern challenges the assumption that greater credit exposure relative to income consistently corresponds to greater repayment risk.

### Risk Interpretation

Credit-to-income ratio alone may not adequately capture borrower repayment capacity. Applicants requesting larger loans relative to their income may differ in employment stability, existing financial obligations, credit history, or other characteristics.

The results suggest that credit-to-income ratio should be evaluated alongside additional financial indicators, with particular attention to potential non-linear relationships and interactions.

## 3. Income-Level Segmentation

**Objective:** Evaluate differences in repayment difficulty across borrower income levels.

Applicants were divided into five income quintiles using reported annual income.

| Quintile | Avg. Income | Avg. Credit | Difficulty Rate |
|---|---:|---:|---:|
| 1 | 77,327 | 384,695 | 8.18% |
| 2 | 117,029 | 496,709 | 8.72% |
| 3 | 146,600 | 579,601 | 8.53% |
| 4 | 192,248 | 683,154 | 8.12% |
| 5 | 310,788 | 850,975 | 6.80% |

### Findings

The highest-income quintile exhibited the lowest observed payment-difficulty rate at 6.80%, while the second income quintile recorded the highest rate at 8.72%.

This represents a difference of 1.92 percentage points between the two groups.

Average credit amounts also increased across income quintiles, from approximately 384,695 in the lowest-income group to 850,975 in the highest-income group.

Despite receiving substantially larger credit amounts on average, applicants in the highest-income quintile exhibited lower observed difficulty rates.

### Risk Interpretation

These findings suggest that income and requested credit should not be interpreted independently. Higher income may be associated with greater capacity to manage larger repayment obligations, but this relationship cannot be established causally from the descriptive analysis.

Income-related variables may provide useful predictive information when combined with payment obligations, existing credit exposure, and repayment history.

## 4. Annuity-to-Income Ratio Analysis

**Objective:** Evaluate whether larger scheduled loan payment amounts relative to income are associated with repayment difficulties.

| Quintile | Avg. Annuity/Income | Difficulty Rate |
|---|---:|---:|
| 1 | 0.076 | 7.20% |
| 2 | 0.124 | 7.83% |
| 3 | 0.163 | 8.13% |
| 4 | 0.214 | 8.70% |
| 5 | 0.327 | 8.51% |

### Findings

Payment-difficulty rates generally increased with annuity-to-income ratios across the first four quintiles.

The observed rate rose from 7.20% in the lowest quintile to 8.70% in the fourth quintile, an increase of 1.50 percentage points.

The highest quintile experienced a slightly lower rate of 8.51%, indicating that the relationship was not strictly monotonic.

### Risk Interpretation

The results suggest that scheduled payment obligations relative to income may be an informative feature for credit risk modeling.

However, the ratio only captures the application's annuity amount relative to reported income and does not account for all existing debt obligations.

Further analysis is necessary to determine its incremental predictive value beyond income and credit amount.

## 5. Employment Duration Analysis

**Objective:** Examine the relationship between employment history and observed repayment difficulties.

| Employment Duration | Applicants | Difficulty Rate |
|---|---:|---:|
| Less than 1 year | 27,982 | 10.97% |
| 1–3 years | 61,472 | 11.07% |
| 3–5 years | 46,902 | 9.67% |
| 5–10 years | 64,871 | 7.37% |
| 10+ years | 50,910 | 5.19% |
| Sentinel value | 55,374 | 5.40% |

### Findings

Employment duration demonstrated the clearest directional association with observed payment difficulties among the four segmentation analyses.

Applicants employed for 1–3 years exhibited the highest difficulty rate at 11.07%, compared with 5.19% among applicants employed for more than 10 years.

This represents a **5.88-percentage-point difference**, with the shorter-employment group experiencing approximately 2.13 times the observed difficulty rate.

Difficulty rates generally decreased with longer employment duration, particularly beyond three years.

The dataset also contained 55,374 records with a special employment-duration value of `365243`. These records were analyzed separately and exhibited a 5.40% payment-difficulty rate.

### Risk Interpretation

The findings suggest that employment duration may be a useful candidate predictor when combined with other borrower characteristics.

However, employment history may correlate with age, income, and other socioeconomic factors. Additional statistical analysis is needed to determine whether its apparent relationship remains after accounting for these variables.

The sentinel value should not be interpreted as a literal employment duration. Its meaning and relationship with other applicant characteristics should be investigated before feature engineering.

## 6. Key Analytical Conclusions

The four segmentation analyses reveal important differences in how borrower characteristics relate to repayment difficulties.

**Employment stability:** Longer recorded employment histories were associated with substantially lower observed payment-difficulty rates.

**Financial capacity:** Applicants in the highest-income group exhibited lower difficulty rates despite having larger average credit amounts.

**Non-linear financial relationships:** Credit-to-income and annuity-to-income ratios did not demonstrate consistently increasing risk across all quintiles, emphasizing the importance of analyzing interactions between financial indicators.

**Data quality:** Special numerical encodings, particularly the employment-duration sentinel value, require deliberate preprocessing to avoid misleading model interpretations.

These findings support developing a multivariable predictive modeling approach rather than relying on individual financial thresholds.

## 7. Limitations

This analysis is descriptive and does not establish causal relationships between borrower characteristics and repayment difficulties.

Observed differences may be influenced by unmeasured variables, correlations between borrower characteristics, and selection effects within the loan application data.

Quintile comparisons do not establish the statistical significance or independent predictive importance of individual features. Additional validation, including multivariable modeling and out-of-sample evaluation, is required.

Employment and income characteristics should also be evaluated carefully for potential fairness implications before considering their use in real lending decisions.

## 8. Next Steps

The next stage will incorporate historical credit information from `bureau.csv` to expand the feature set beyond application-level financial characteristics.

Planned activities include:

- Aggregating previous credit accounts and outstanding debt at the applicant level.
- Engineering credit-history features, including credit exposure and account activity.
- Integrating historical credit summaries with application-level financial data.
- Investigating missing credit history and potential data leakage.
- Preparing the resulting dataset for baseline predictive modeling.

**Tools:** SQL, DuckDB, Python, pandas, matplotlib

**Project:** Home Credit Default Risk — Borrower Segmentation and Financial Risk Analysis
