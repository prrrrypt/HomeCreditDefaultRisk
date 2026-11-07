# Day 4 — Historical Credit Feature Engineering

## Objective

Integrate historical credit bureau records with application-level financial data to construct a richer dataset for credit risk modeling.

## Methodology

Historical credit records were aggregated at the applicant level using DuckDB and SQL.

Engineered features included credit account counts, active and closed account counts, outstanding debt, credit exposure, delinquency measures, credit history recency, and debt-to-credit ratios.

The aggregated credit information was joined to application data using `SK_ID_CURR`, preserving one row per application.

## Data Validation

- Original applications: 307,511
- Joined applications: [Insert actual count]
- Duplicate applicant IDs: [Insert count]
- Applicants with bureau history: [Insert count]
- Applicants without bureau history: [Insert count]

## Exploratory Findings

### Bureau Coverage

[Describe the percentage of applicants with recorded bureau history and how observed payment-difficulty rates differ.]

### Credit Account Activity

[Describe the relationship between bureau account counts and observed payment difficulty.]

### Missing Data

[Summarize missingness in engineered features and distinguish unavailable historical records from missing credit balances.]

## Technical Considerations

- Maintained applicant-level data granularity by aggregating bureau records before joining.
- Preserved missing values where unavailable credit history could not be equated with zero financial exposure.
- Handled special employment-duration encodings explicitly.
- Identified timing, feature leakage, and potential fairness considerations for later modeling.

## Next Steps

Establish reproducible training and evaluation splits, build a baseline logistic regression classifier, and evaluate initial predictive performance using metrics appropriate for imbalanced data.

## Tools

Python, DuckDB, SQL, pandas, matplotlib, Parquet.