# Day 7 — Model Robustness, Cross-Validation & Bureau Feature Ablation

## 1. Executive Summary

This phase assessed the stability and generalization of the LightGBM credit risk classifier and measured the incremental predictive value of the applicant-level historical credit bureau features engineered during Day 4. Results are based on stratified cross-validation of the original training partition and a separate training-versus-validation comparison; the held-out test partition was not evaluated in this phase.

**Key findings:**

- Three-fold cross-validation produced a mean **ROC-AUC of 0.7466 ± 0.0028**, **Average Precision of 0.2317 ± 0.0028**, and **Brier Score of 0.06844 ± 0.00014** (mean ± sample standard deviation).
- The model performed better on training than validation data (**ROC-AUC 0.7852 vs. 0.7541**; **Average Precision 0.2854 vs. 0.2373**), indicating some overfitting.
- Adding historical bureau features improved mean **ROC-AUC by 0.0065**, **Average Precision by 0.0115**, and reduced **Brier Score by 0.00046**, compared with using application features alone.
- The full feature set outperformed the application-only feature set on **all three metrics in every tested fold**, suggesting a repeatable benefit within this experimental design.

The results favor retaining bureau-derived features for subsequent model development, while motivating further regularization, feature-provenance checks, and independent final testing.

## 2. Experimental Design

The analysis used the Home Credit Default Risk labeled application data and the engineered feature table from Day 4. The candidate predictor set matched the Day 6 LightGBM experiment. Data preprocessing was fitted separately within each training fold to prevent fold-level preprocessing leakage.

Three experiments were conducted:

1. **Stratified three-fold cross-validation** on the original training partition to estimate performance stability.
2. **Training-versus-validation evaluation** to inspect potential overfitting.
3. **Paired feature ablation**, comparing application-only predictors with the same predictors plus engineered bureau history features on identical folds.

The LightGBM configuration used **524 boosting iterations**, selected during Day 6 using the existing validation partition. As a result, the reported CV experiment is a useful robustness check but is **not a fully nested or independent model-selection evaluation**.

## 3. Cross-Validation Stability

| Fold | ROC-AUC | Average Precision | Brier Score |
|---|---:|---:|---:|
| 1 | 0.7476 | 0.2286 | 0.06854 |
| 2 | 0.7488 | 0.2343 | 0.06828 |
| 3 | 0.7434 | 0.2322 | 0.06850 |
| **Mean** | **0.7466** | **0.2317** | **0.06844** |
| **Sample standard deviation** | **0.0028** | **0.0028** | **0.00014** |

### Interpretation

The ROC-AUC across folds ranged from **0.7434 to 0.7488**, a narrow spread of approximately **0.0054**. Average Precision ranged from **0.2286 to 0.2343**. The small standard deviations indicate relatively consistent results across these three stratified partitions.

The cross-validation mean ROC-AUC (**0.7466**) is lower than the Day 6 validation ROC-AUC (**0.7541**). These numbers are not directly comparable estimates of the same training procedure: individual CV models were trained on only two-thirds of the original training partition, while the Day 6 model was trained on all of that partition, with its boosting iteration chosen using the validation data.

The stability across three folds is encouraging but does not demonstrate robustness to temporal shifts, different applicant populations, or changes in credit reporting.

## 4. Training-versus-Validation Performance

| Metric | Training | Validation | Training minus validation |
|---|---:|---:|---:|
| ROC-AUC | 0.7852 | 0.7541 | +0.0311 |
| Average Precision | 0.2854 | 0.2373 | +0.0481 |
| Brier Score | 0.06605 | 0.06806 | −0.00202 |

### Interpretation

The model achieves higher ROC-AUC and Average Precision on training observations than on validation observations, consistent with **some degree of overfitting**. The Average Precision gap of approximately **0.0481** is especially worth investigating, as identifying the minority positive class is a central modeling objective.

The lower training Brier Score indicates smaller probability prediction errors on the training set. This is consistent with the discrimination gap, although Brier Score alone does not fully establish calibration quality.

Potential next steps include simplifying tree complexity, adjusting regularization, tuning iterations within training folds, and evaluating whether those changes reduce the performance gap without degrading out-of-fold prediction quality.

## 5. Historical Bureau Feature Ablation

To estimate the incremental value of Day 4's feature engineering, the experiment evaluated two LightGBM configurations on identical folds:

- **Application Only:** Selected financial, employment, categorical, and external-source features from application data.
- **Application + Bureau:** The same features plus historical credit bureau aggregates and the bureau-history availability indicator.

### Cross-validation means

| Metric | Application Only | Application + Bureau | Full minus application-only |
|---|---:|---:|---:|
| ROC-AUC | 0.7401 | **0.7466** | **+0.0065** |
| Average Precision | 0.2202 | **0.2317** | **+0.0115** |
| Brier Score | 0.06890 | **0.06844** | **−0.00046** |

Adding bureau history produced a **5.23% relative gain in Average Precision** and a **0.88% relative gain in ROC-AUC** compared with the application-only configuration. The Brier Score decreased by approximately **0.67%** in relative terms, where lower is better.

### Paired fold-level changes

| Fold | Δ ROC-AUC | Δ Average Precision | Δ Brier Score |
|---|---:|---:|---:|
| 1 | +0.0059 | +0.0105 | −0.00041 |
| 2 | +0.0067 | +0.0112 | −0.00046 |
| 3 | +0.0069 | +0.0128 | −0.00052 |

### Interpretation

The full feature set improved all three metrics in **each of the three paired folds**, providing evidence that the historical credit aggregates add predictive value under the chosen model and validation setup.

This is a measurable outcome of the SQL feature engineering pipeline, but the size of the gains is modest. The experiment does not establish which specific bureau feature is responsible, whether the improvement is statistically significant in a broader population, or whether it would persist under out-of-time validation. The compared models used identical model parameters rather than separately optimized parameters for each feature set.

## 6. Data Integrity and Leakage Considerations

The notebook's methodology uses distinct training, validation, and held-out test partitions. Preprocessing is fitted separately for each cross-validation fold. This guards against a common form of leakage from imputation and categorical encoding.

Nevertheless, partition isolation does **not** prove that all predictors were available at the original application date. Before operational interpretation, review the original timing and provenance of bureau information and external-source scores, confirm that aggregation does not introduce post-application information, and investigate sensitive or proxy features.

The uploaded CSV outputs contain evaluation metrics, **not logs of the identifier-overlap assertions or detailed feature-provenance checks**. Those checks should remain visible in the executed notebook and be verified independently; they cannot be confirmed from these CSV files alone.

## 7. Conclusions

The Day 7 results support three conclusions:

1. **Reasonable within-sample resampling stability:** LightGBM maintained similar ROC-AUC, Average Precision, and Brier Scores across three stratified folds.
2. **Some overfitting remains:** Training performance exceeded validation performance, indicating that model complexity and generalization deserve further investigation.
3. **Bureau features contributed measurable incremental value:** Historical credit features improved all three evaluated metrics across every paired fold, making Day 4's relational data engineering an empirically supported part of the pipeline.

These conclusions are based on the current development data and should not be interpreted as independent evidence of real-world lending performance.

## 8. Limitations and Next Steps

The model's 524 iterations were previously selected using the development validation set, and cross-validation covers only three folds within the original training partition. The analysis does not provide confidence intervals for population performance, nested hyperparameter-selection estimates, or temporal validation. No final held-out test results are reported here.

The next phase will investigate SHAP explanations for global and individual model predictions and examine whether key risk variables have interpretable, stable associations with model output. Model-selection and calibration decisions should be finalized before opening the held-out test set.

**Tools:** Python, DuckDB, pandas, scikit-learn, LightGBM, NumPy, matplotlib.

**Source files:** `day07_cross_validation.csv`, `day07_overfitting_analysis.csv`, `day07_feature_ablation.csv`, `day07_ablation_summary.csv`.
