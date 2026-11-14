# Home Credit Default Risk | End-to-End Risk Analytics

**SQL feature engineering · Predictive modeling · Model explainability · Decision analytics · Interactive dashboard**

### Live Dashboard

**[Explore the Interactive Credit Risk Dashboard](https://homecreditdefaultrisk.streamlit.app)**

Explore held-out model evaluation, risk segmentation,
SHAP explainability, and hypothetical review-cost scenarios.

An end-to-end credit risk analytics portfolio project using the [Home Credit Default Risk dataset](https://www.kaggle.com/competitions/home-credit-default-risk). The project combines SQL-based credit history aggregation, Python exploratory analysis, interpretable and gradient-boosted classifiers, SHAP explanations, risk segmentation, and a Streamlit dashboard.

The goal is to understand **which financial and credit-history characteristics are associated with recorded repayment difficulty**, how well models rank higher-risk applications, and how evaluation results translate into *illustrative* review-capacity tradeoffs. This is an educational analysis, **not** a production lending system.

> **Evaluation status:** All predictive performance figures below are from the **validation partition**. The held-out test set is reserved for final evaluation; its results are not reported here.

## Key results

| Finding | Validation / analysis result |
|---|---:|
| LightGBM ROC-AUC | **0.7541** |
| LightGBM average precision | **0.2373** |
| Logistic Regression ROC-AUC | 0.7441 |
| Logistic Regression average precision | 0.2208 |
| LightGBM Brier score | **0.0681** |
| Observed difficulty rate in highest risk decile | **27.13%** |
| Lift in highest risk decile | **3.36×** |
| Positive cases captured in top 20% of risk scores | **51.80%** |
| Relative improvement in cross-validation average precision from adding bureau features | **5.23%** |

**Key takeaway:** LightGBM produced better ranking metrics than the Logistic Regression baseline on the validation set. At an approximately 10% review capacity, its highest-scoring applications contained **33.62% of all observed positive cases**. Historical bureau features provided measurable incremental predictive value in a three-fold feature ablation experiment.

These are associations and historical predictive results, not evidence that reviewing or denying a particular application prevents a loss.

## Interactive dashboard

The Streamlit dashboard brings the analysis into a single, business-oriented interface, with sections for:

- **Model overview:** ROC-AUC, average precision, and Brier score comparisons.
- **Risk segmentation:** observed vs. predicted difficulty by decile, lift, and cumulative gains.
- **Financial segments:** subgroup analyses by income, annuity burden, and bureau-history availability.
- **Review scenarios:** threshold and capacity comparisons with adjustable *hypothetical* review and missed-case costs.
- **Explainability:** global SHAP feature importance.

**Run locally:**

```bash
conda env create -f environment.yml
conda activate homecredit
python -m streamlit run dashboard/app.py
```

If the `homecredit` environment already exists, use `conda activate homecredit` rather than creating it again. Ensure Streamlit and Plotly are installed in that environment; their dependencies should be reflected in `environment.yml`.

**Live dashboard:** Not yet linked. Add the public Streamlit URL here after deployment and verification.

The dashboard is designed around **aggregated CSV reports** rather than raw applicant records or a deployed prediction endpoint. Its cost scenarios are illustrative and do not make credit decisions.

## Data

**Source:** [Kaggle — Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk)

The project begins with `application_train.csv` and aggregates historical credit information from `bureau.csv`.

| Source | Size | Role |
|---|---:|---|
| `application_train.csv` | 307,511 applications | Labeled applicant-level outcomes and application features |
| `bureau.csv` | 1,716,428 records | Historical credit-account features aggregated by applicant |

The target variable, `TARGET`, denotes the dataset's recorded payment-difficulty outcome. The positive class represents approximately **8.07%** of labeled applications, creating an imbalanced classification problem.

Raw and processed datasets are excluded from version control. Download the dataset from Kaggle and place the required source CSV files under `data/raw/` before reproducing the data preparation notebooks.

## Workflow and methodology

### 1. Exploratory analysis and SQL segmentation

Used **DuckDB, SQL, and pandas** to examine target imbalance, missing values, outliers, income and repayment burden, employment duration, and historical credit coverage.

Selected observations:

- The target distribution is approximately **91.93% negative / 8.07% positive**.
- Historical payment-difficulty rates vary across employment-duration groups and financial-burden quintiles; several relationships are **non-monotonic**.
- Among labeled applications, borrowers without a matched bureau history had an observed difficulty rate of approximately **10.12%**, compared with **7.73%** for those with bureau history. This association does not establish causation.

### 2. Credit bureau feature engineering

Aggregated bureau records to one row per applicant using SQL and joined the results to application data. Features include historical account counts, active and closed accounts, total credit and debt, overdue amounts, credit age, and debt-to-credit ratios.

Additional financial variables include credit-to-income, annuity-to-income, employment duration, and a flag for the special `DAYS_EMPLOYED` sentinel value.

**Integrity checks:** The engineered modeling table retained **307,511 unique applicant rows**, without introducing duplicate application identifiers.

### 3. Predictive modeling

Trained an interpretable **Logistic Regression** benchmark and a **LightGBM** gradient-boosted classifier on the same original feature set, preprocessing design, and stratified partitions.

| Partition | Applications |
|---|---:|
| Training | 184,506 |
| Validation | 61,502 |
| Held-out test | 61,503 |

The pipeline uses 27 original predictors (22 numerical, 5 categorical), with imputation, numerical scaling, and one-hot encoding. Model comparisons use probabilities rather than relying only on a default classification threshold.

| Metric | Logistic Regression | LightGBM |
|---|---:|---:|
| ROC-AUC | 0.7441 | **0.7541** |
| Average precision | 0.2208 | **0.2373** |
| Brier score (lower is better) | 0.0688 | **0.0681** |
| Precision among top 10% scores | 25.78% | **27.13%** |
| Recall among top 10% scores | 31.94% | **33.62%** |

LightGBM used regularization and validation-based early stopping; the selected model stopped at **524 boosting iterations**. Since the validation partition was used during model development, results on that partition may be optimistic.

### 4. Robustness and feature ablation

A three-fold stratified analysis on the original training partition yielded:

| Metric | Mean across folds |
|---|---:|
| ROC-AUC | 0.7466 |
| Average precision | 0.2317 |
| Brier score | 0.0684 |

Ablation experiments compared application-only predictors with application **plus bureau-derived features**. Including bureau features improved mean ROC-AUC from approximately **0.7401 to 0.7466**, and mean average precision from **0.2202 to 0.2317** (approximately **5.23% relative improvement**). The full feature set also improved Brier score.

The training-versus-validation performance gap indicates some overfitting remains. These are exploratory robustness checks, not a substitute for independent test evaluation or out-of-time validation.

### 5. Explainability with SHAP

Used **Tree SHAP** on a reproducible 1,000-application sample from the validation partition to investigate global feature importance, feature effects, selected individual predictions, and bureau feature contributions.

The largest individual mean absolute SHAP contributions came from `EXT_SOURCE_2`, `EXT_SOURCE_3`, and `EXT_SOURCE_1`, followed by employment and loan-related characteristics. A bureau debt-to-credit ratio also ranked among leading transformed features.

Explanations were computed in **raw log-odds**, not probability percentage points. SHAP explains the fitted model's behavior, **not the causal impact** of an applicant characteristic on repayment outcomes.

### 6. Risk deciles and cumulative gains

Ranked validation applications by LightGBM score and grouped them into ten approximately equal-sized deciles.

| Measure | Result |
|---|---:|
| Lowest-decile observed difficulty | 1.58% |
| Highest-decile observed difficulty | **27.13%** |
| Highest-decile lift vs. overall rate | **3.36×** |
| Positive cases captured in top 10% | 33.62% |
| Positive cases captured in top 20% | **51.80%** |
| Positive cases captured in top 30% | 64.75% |

Observed repayment-difficulty rates increased across the ranked deciles. Predicted and observed rates also tracked relatively closely at the decile level; this is encouraging but does not establish calibration on future populations.

### 7. Threshold and hypothetical cost analysis

Compared probability thresholds with fixed-capacity rankings. The illustrative cost function was:

```text
Modeled cost = (applications reviewed × cost per review)
             + (unflagged positive cases × cost per missed case)
```

Under **illustrative** assumptions of 25 cost units per review and 500 units per missed positive case, a threshold of **0.06** minimized cost *among the tested probability thresholds* on the validation data, flagging 27,951 applications and capturing 78.45% of positive cases.

Varying the missed-case penalty changed the preferred threshold substantially. These numbers are **not actual losses, measured savings, or a validated decision policy**: the analysis assumes that flagging a historical positive case avoids its modeled penalty, which has not been demonstrated.

For hard review-capacity limits, the notebook uses integer applicant counts to avoid exceeding a stated limit through rounding. Capacity-based results should be regenerated and checked before publication if the source CSV still reflects older ceiling-rounded counts.

## Project structure

```text
HomeCreditDefaultRisk/
├── .streamlit/
│   └── config.toml                 # Optional dashboard theme
├── dashboard/
│   ├── app.py                      # Streamlit application
│   └── requirements.txt            # Dashboard-only dependencies
├── data/
│   ├── raw/                         # Kaggle files; gitignored
│   └── processed/                   # Engineered parquet; gitignored
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_borrower_risk.ipynb
│   ├── 03_credit_history_features.ipynb
│   ├── 04_baseline_model.ipynb
│   ├── 05_lightgbm_model.ipynb
│   ├── 06_model_robustness.ipynb
│   ├── 07_shap_explainability.ipynb
│   ├── 08_risk_segmentation.ipynb
│   └── 09_decision_analysis.ipynb
├── sql/                             # SQL exploratory and feature engineering scripts
├── reports/                         # Findings, aggregate CSV metrics, and figures
├── models/                          # Locally saved models; gitignored
├── src/                             # Supporting code (as developed)
├── tests/                           # Validation tests (as developed)
├── environment.yml                  # Conda project environment
└── README.md
```

Some local directories may not appear on GitHub if empty or excluded by `.gitignore`.

## Reproduce the analysis

1. **Clone the repository.**

   ```bash
   git clone https://github.com/prrrrypt/HomeCreditDefaultRisk.git
   cd HomeCreditDefaultRisk
   ```

2. **Create and activate the Conda environment.**

   ```bash
   conda env create -f environment.yml
   conda activate homecredit
   ```

3. **Download the data** from the Kaggle competition page and put the source files in `data/raw/`. Follow the dataset's licensing and access terms.

4. **Run the notebooks in numerical order**, beginning with exploratory analysis and feature engineering. The later notebooks expect the locally generated `data/processed/modeling_features.parquet`; dashboard source tables are generated by the corresponding analysis notebooks.

5. **Launch the dashboard** after the aggregate report CSVs have been generated:

   ```bash
   python -m streamlit run dashboard/app.py
   ```

For a dashboard-only deployment, use `dashboard/requirements.txt` and ensure the aggregate CSVs referenced by `dashboard/app.py` are committed. The dashboard is intended to operate without raw applicant-level datasets or serialized model artifacts.

## Tools and skills

**Languages & querying:** Python, SQL, DuckDB  
**Data processing:** pandas, NumPy, Parquet  
**Machine learning:** scikit-learn, LightGBM  
**Evaluation:** ROC-AUC, average precision, calibration, cross-validation, ablation, lift, cumulative gains  
**Explainability:** SHAP  
**Visualization & delivery:** matplotlib, Plotly, Streamlit, Jupyter, Git/GitHub

## Limitations and responsible use

- Results are based on historical data and a validation partition used during model development; **no final held-out test metrics are reported**.
- Random stratified splits do not establish out-of-time or out-of-population stability.
- Financial and external-source fields may encode sensitive proxy relationships; feature provenance, point-in-time availability, fairness, and legal compliance require additional review.
- SHAP values and subgroup associations are not causal explanations.
- Review-cost scenarios are hypothetical, and model predictions do not demonstrate that interventions avoid losses.
- The model is **not intended for automated credit approvals, denials, or adverse-action decisions**.

## Project Status

**Status: Complete — 14-Day End-to-End Credit Risk Analytics Project**

The project includes data exploration, SQL-based feature engineering, predictive modeling, cross-validation, SHAP explainability, risk segmentation, cost-sensitive analysis, and final held-out evaluation.

**Final results:**
- LightGBM achieved **0.7487 ROC-AUC** and **0.2329 Average Precision** on 61,503 held-out applications.
- LightGBM improved Average Precision by approximately **6.9%** over Logistic Regression.
- The highest-risk 20% of test applications captured **50.03% of recorded repayment-difficulty cases**.
- The Streamlit dashboard presents model performance, risk segmentation, hypothetical review scenarios, and explainability.

**[Explore the Live Dashboard](https://homecreditdefaultrisk.streamlit.app/)**

### Potential Future Improvements

While the initial project is complete, potential extensions include:

- **Temporal validation:** Evaluate performance across different application periods.
- **Fairness assessment:** Investigate disparities and proxy effects across relevant borrower groups, subject to available data and responsible evaluation practices.
- **Probability calibration:** Explore calibration improvements using separate development data.
- **Model monitoring:** Develop methods to detect data drift and changes in predictive performance over time.
- **Business validation

---

**Dataset:** [Home Credit Default Risk — Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk)  
**Repository:** [prrrrypt/HomeCreditDefaultRisk](https://github.com/prrrrypt/HomeCreditDefaultRisk)
