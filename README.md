# Home Credit Default Risk | Credit Risk Analytics

An end-to-end **credit risk analytics** portfolio project investigating repayment difficulties using financial data, SQL, and Python. The current phase focuses on exploratory analysis and interpretable borrower segmentation; predictive modeling and a dashboard are planned.

**Dataset:** [Home Credit Default Risk (Kaggle)](https://www.kaggle.com/competitions/home-credit-default-risk/data)  
**Status:** Days 1–3 completed · feature engineering and modeling in progress

## Project objectives

- Investigate associations between borrower characteristics and payment difficulties.
- Use DuckDB and SQL to develop reproducible financial-risk analyses.
- Engineer applicant-level features from historical credit data.
- Compare statistical and machine-learning classification models, with careful out-of-sample evaluation.
- Examine model explainability, risk thresholds, calibration, and decision trade-offs.
- Build a portfolio dashboard summarizing findings and results.

## Dataset and target

The main labeled table, `application_train.csv`, contains **307,511 applications** and **122 columns**. The target, `TARGET`, identifies the dataset's defined repayment-difficulty outcome (`1`) versus its absence (`0`); it should not be interpreted as a universal definition of loan default. The positive class comprises approximately **8.07%** of applications.

This dataset contains sensitive financial and demographic attributes. Findings are exploratory and should not be used to make real lending decisions.

## Findings so far: Days 2–3

The Day 3 analyses use SQL Common Table Expressions, `NTILE()` window functions, and aggregate payment-difficulty rates. The figures below are descriptive rates from notebook outputs, **not causal effects or predictive model performance**.

| Analysis | Observed finding |
| --- | --- |
| Credit-to-income ratio | Difficulty peaked at **8.93%** in the middle ratio quintile, compared with **7.33%** in the lowest and **7.25%** in the highest quintile; the relationship was non-linear. |
| Income quintiles | The highest-income quintile had a **6.80%** difficulty rate, versus **8.72%** in the second quintile. |
| Annuity-to-income ratio | Difficulty increased from **7.20%** in the lowest quintile to **8.70%** in the fourth, then eased to **8.51%** in the fifth. |
| Employment duration | The observed rate was **11.07%** for 1–3 years of employment versus **5.19%** for 10+ years. |

### Interpretation

- **No single financial ratio tells the whole story.** The credit-to-income pattern is non-monotonic, suggesting that multivariable analysis will be important.
- **Income and requested credit should be considered together.** Higher-income applicants had larger average requested credit amounts but lower observed difficulty at the top end of the income distribution.
- **Employment history is associated with differences in outcomes,** though other borrower characteristics may confound the relationship.
- **Data quality affects interpretation.** The `DAYS_EMPLOYED = 365243` sentinel value must be treated separately from ordinary employment duration.

**Reproducibility note:** SQL `NTILE()` queries should order by a unique identifier (for example, `ORDER BY credit_income_ratio, SK_ID_CURR`) to handle tied ratios deterministically. Slight changes in reported quintile values are possible after rerunning corrected queries.

See the detailed analysis in [`notebooks/02_borrower_risk.ipynb`](notebooks/02_borrower_risk.ipynb) and the SQL in [`sql/02_borrower_risk_analysis.sql`](sql/02_borrower_risk_analysis.sql). A narrative findings report can be added at `reports/day03_risk_findings.md`.

## Technology stack

**Used so far:** Python, pandas, NumPy, SQL, DuckDB, Jupyter, matplotlib / seaborn.  
**Planned:** scikit-learn, LightGBM, SHAP, Streamlit.

## Repository structure

```text
HomeCreditDefaultRisk/
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_borrower_risk.ipynb
├── sql/
│   ├── 01_exploratory_analysis.sql
│   └── 02_borrower_risk_analysis.sql
├── reports/
├── src/
├── dashboard/
├── tests/
├── data/                 # Local only; not committed
├── requirements.txt
└── README.md
```

## Getting started

1. Download the dataset from the [Kaggle competition page](https://www.kaggle.com/competitions/home-credit-default-risk/data) after accepting the applicable rules.
2. Place `application_train.csv` in `data/raw/` (and additional tables there as needed).
3. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

4. Open `notebooks/01_exploration.ipynb`, followed by `notebooks/02_borrower_risk.ipynb`. Select the project's `.venv` kernel and run the cells from the top.

Notebook paths assume they are executed from the `notebooks/` folder or the repository root. Raw dataset files are intentionally excluded from version control.

## Roadmap

| Phase | Status | Goal |
| --- | --- | --- |
| Setup and environment | Complete | Repository structure and dependencies |
| Exploratory data analysis | Complete | Target distribution, data quality, missingness |
| Borrower segmentation with SQL | Complete | Financial ratios, income and employment analysis |
| Historical credit feature engineering | Next | Aggregate `bureau.csv` data at applicant level |
| Baseline and advanced modeling | Planned | Logistic regression and gradient boosting |
| Explainability and decision analysis | Planned | Calibration, SHAP, and threshold trade-offs |
| Interactive dashboard | Planned | Summarize portfolio-level risk analytics |

## Limitations and responsible use

The dataset describes historical payment-difficulty labels, not a complete measure of creditworthiness. Group-level associations do not establish causation. Subsequent modeling should address class imbalance, leakage, missing data, reproducibility, calibration, and fairness considerations. In particular, applicant age and other sensitive or proxy variables warrant careful evaluation rather than automatic deployment in any decision-making process.

## Data attribution

Source: [Home Credit Default Risk, Kaggle competition](https://www.kaggle.com/competitions/home-credit-default-risk/data). Dataset files are not redistributed in this repository; use is subject to the competition's applicable rules.
