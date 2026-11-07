# Day 4 — Historical Credit Feature Engineering & Risk Analysis

## 1. Executive Summary

This phase expanded the Home Credit Default Risk analysis by integrating historical credit bureau records with application-level financial data to develop a more comprehensive borrower risk assessment dataset.

Using DuckDB and SQL, 1,716,428 historical credit records were aggregated into applicant-level financial features, including credit account activity, outstanding debt, historical delinquency, credit exposure, and credit utilization indicators.

The aggregated features were joined with 307,511 loan applications while preserving the original dataset structure and target distribution.

**Key findings:**

- Applicants without recorded bureau history exhibited a **10.12% payment-difficulty rate**, compared with **7.73%** among applicants with bureau history.
- Applicants with 3–5 historical credit accounts had the lowest observed difficulty rate at **7.40%**.
- The relationship between credit account count and payment difficulties was non-linear, indicating that more historical credit accounts do not necessarily correspond to higher observed risk.
- Feature engineering successfully preserved all 307,511 applications without introducing duplicate applicant records.

These results support incorporating historical credit information into subsequent predictive modeling.

## 2. Historical Credit Data Overview

The `bureau.csv` dataset contains historical credit records reported by other financial institutions.

| Metric | Value |
|---|---:|
| Total historical credit records | 1,716,428 |
| Unique applicants in bureau dataset | 305,811 |
| Unique credit account IDs | 1,716,428 |
| Labeled applications | 307,511 |

The bureau dataset contains multiple credit records per applicant, making direct joins unsuitable for applicant-level predictive modeling without aggregation.

To address this, historical credit information was summarized using `SK_ID_CURR` as the grouping key.

The 305,811 unique applicants in the bureau dataset are not all necessarily present in the labeled training applications. The resulting join matched 263,491 labeled applicants to bureau records.

## 3. Financial Feature Engineering

Historical credit records were aggregated into applicant-level financial indicators using SQL Common Table Expressions, conditional aggregation, and summary statistics.

The engineered variables included:

| Feature | Description |
|---|---|
| `bureau_total_accounts` | Number of historical credit accounts |
| `bureau_active_accounts` | Number of active credit accounts |
| `bureau_closed_accounts` | Number of closed credit accounts |
| `bureau_total_credit` | Total reported historical credit amounts |
| `bureau_total_debt` | Total reported outstanding debt |
| `bureau_total_overdue` | Total reported overdue amounts |
| `bureau_max_days_overdue` | Maximum reported days overdue |
| `bureau_avg_days_since_credit` | Average credit account age |
| `bureau_debt_credit_ratio` | Outstanding debt relative to reported credit amounts |
| `has_bureau_history` | Indicator for available bureau credit records |

Additional application-level financial variables were calculated, including credit-to-income ratio, annuity-to-income ratio, age, and employment duration.

An employment sentinel flag was introduced to preserve information associated with specially encoded employment-duration values without interpreting them as literal employment history.

### Technical approach

A one-to-many relationship between applicants and bureau accounts was transformed into a one-to-one applicant-level feature table before joining.

This approach prevented duplicate borrower records and maintained the integrity of the target variable for predictive modeling.

## 4. Data Integration Validation

The aggregated bureau features were joined to the main application dataset through a left join on `SK_ID_CURR`.

### Join validation results

| Validation Metric | Result |
|---|---:|
| Original labeled applications | 307,511 |
| Applications after joining | 307,511 |
| Unique applicant IDs | 307,511 |
| Duplicate applicant IDs | 0 |

**Validation status: PASSED**

The final joined dataset retained exactly one row per labeled applicant, demonstrating that the bureau aggregation did not introduce duplicate applications.

### Target distribution preservation

| Target | Applicants | Percentage |
|---|---:|---:|
| 0 — No recorded payment difficulty | 282,686 | 91.93% |
| 1 — Recorded payment difficulty | 24,825 | 8.07% |

The target distribution remained unchanged after the join.

This confirms that the data integration preserved the original labeled population, a critical requirement for reliable downstream model training.

## 5. Credit Bureau Coverage Analysis

**Objective:** Investigate whether the availability of historical bureau records is associated with observed payment difficulties.

| Bureau History | Applicants | Difficulty Rate |
|---|---:|---:|
| No bureau records | 44,020 | 10.12% |
| Bureau records available | 263,491 | 7.73% |

### Findings

Approximately **85.69%** of labeled applicants had historical credit bureau records, while **14.31%** had no matching bureau records.

Applicants without recorded bureau history exhibited a 10.12% payment-difficulty rate, compared with 7.73% among applicants with recorded bureau history.

This represents a **2.39-percentage-point difference**, with the group lacking bureau records exhibiting approximately 31% higher observed difficulty rates in relative terms.

### Risk interpretation

The results indicate that bureau history availability is associated with differences in repayment outcomes.

However, missing bureau records should not automatically be interpreted as poor credit history. The absence of matching records may reflect limited credit activity, reporting coverage, or other data availability factors.

Consequently, the `has_bureau_history` indicator may provide useful predictive information, but its relationship with repayment outcomes requires further investigation alongside other financial and demographic characteristics.

## 6. Missing Data Assessment

**Objective:** Evaluate missingness in the newly engineered historical credit features.

| Engineered Feature | Missing Values |
|---|---:|
| `bureau_debt_credit_ratio` | 17.03% |
| `bureau_total_debt` | 16.71% |
| `bureau_total_credit` | 14.32% |
| `bureau_total_accounts` | 14.31% |
| `bureau_max_days_overdue` | 14.31% |

### Findings

The missingness of several bureau-derived features closely matches the 14.31% of applicants without matching bureau records.

However, total debt and debt-to-credit ratio exhibited additional missingness beyond the unmatched applicant population.

In particular, the debt-to-credit ratio had the highest missingness at 17.03%, approximately 2.71 percentage points above the missing bureau-history proportion.

### Data quality interpretation

Missing financial values cannot always be equated with zero outstanding debt or zero financial exposure.

The analysis therefore preserved missing values to distinguish between unavailable information and observed financial amounts.

The engineered `has_bureau_history` feature provides an additional way to represent differences in data availability.

Future preprocessing will evaluate imputation strategies and missingness indicators within training-only pipelines to prevent data leakage.

## 7. Historical Credit Account Segmentation

**Objective:** Examine whether the number of historical credit accounts is associated with repayment difficulties.

Applicants were grouped according to their total number of bureau credit records.

| Historical Credit Accounts | Applicants | Difficulty Rate |
|---|---:|---:|
| No bureau records | 44,020 | 10.12% |
| 1–2 accounts | 71,707 | 8.20% |
| 3–5 accounts | 86,883 | 7.40% |
| 6–10 accounts | 72,624 | 7.46% |
| 11+ accounts | 32,277 | 8.18% |

### Findings

The results demonstrate a **non-linear relationship** between historical credit account count and observed repayment difficulties.

Applicants with no recorded bureau history exhibited the highest difficulty rate at 10.12%.

Among applicants with bureau records, those with 3–5 accounts showed the lowest observed rate at 7.40%, closely followed by applicants with 6–10 accounts at 7.46%.

Applicants with 11 or more accounts exhibited a somewhat higher difficulty rate of 8.18%.

The difference between applicants with no bureau records and those with 3–5 historical accounts was **2.72 percentage points**.

### Risk interpretation

The results suggest that historical account count alone does not exhibit a consistently increasing or decreasing relationship with repayment difficulties.

A moderate number of recorded credit accounts was associated with lower observed difficulty rates in this dataset, while both fewer and substantially more accounts were associated with somewhat higher rates.

However, historical account counts do not directly measure repayment reliability, financial stability, or creditworthiness.

Additional variables—including active debt, delinquency history, available credit, and account age—may help explain the observed differences.

The non-linear pattern also suggests that flexible modeling techniques or engineered categorical features may be useful during subsequent model development.

## 8. Key Analytical Conclusions

The Day 4 analysis successfully extended application-level financial data with historical credit information while preserving dataset integrity.

**Credit history availability:** Applicants without recorded bureau history exhibited higher observed payment-difficulty rates than those with available historical records.

**Non-linear account relationships:** Applicants with moderate numbers of historical credit accounts demonstrated lower observed difficulty rates than applicants at either end of the account-count distribution.

**Missing information as a modeling consideration:** Unavailable bureau records and missing financial fields require distinct handling, as they do not necessarily represent zero debt or zero credit exposure.

**Data engineering integrity:** Aggregating historical credit records before joining maintained the original 307,511 labeled applications and introduced no duplicate applicant records.

Together, these results suggest that historical credit features may complement the application-level financial indicators analyzed during Days 2 and 3.

## 9. Limitations

This analysis is descriptive and does not establish causal relationships between credit history characteristics and repayment difficulties.

Differences in observed outcomes may reflect other borrower characteristics, reporting practices, or data availability.

Furthermore, historical account counts alone cannot distinguish between responsible repayment activity and substantial existing credit obligations.

The joined dataset has not yet undergone formal predictive model validation. The incremental predictive value of bureau features remains to be established.

Before modeling, the availability and timing of features must also be evaluated to reduce the risk of incorporating information unavailable at the original application date.

## 10. Next Steps — Day 5

The next phase will focus on baseline credit risk prediction.

Planned activities include:

- Establishing reproducible training and test splits.
- Reviewing predictors for target leakage and inappropriate identifiers.
- Developing preprocessing pipelines for missing and categorical data.
- Training a baseline logistic regression classifier.
- Evaluating initial model performance using ROC-AUC, average precision, precision, recall, and confusion matrices.
- Comparing model predictions against the observed payment-difficulty distribution.

**Tools:** Python, DuckDB, SQL, pandas, matplotlib, Parquet.

**Project:** Home Credit Default Risk — Historical Credit Feature Engineering & Risk Analysis.