# Day 10 — Decision Threshold Optimization & Cost-Sensitive Risk Analysis

## 1. Executive Summary

This phase evaluated how LightGBM credit risk predictions could support hypothetical review prioritization under different screening capacities and cost assumptions.

The analysis examined probability thresholds, fixed-capacity screening, confusion-matrix outcomes, and the sensitivity of modeled costs to different review and missed-case penalties.

**Key findings:**

- Under the baseline hypothetical cost assumptions, a probability threshold of **0.06** produced the lowest modeled cost among the evaluated thresholds.
- At this threshold, the model flagged **27,951 applications**, capturing **78.45% of positive cases**.
- The lowest modeled cost on the threshold grid was **1,233,775 hypothetical units**.
- Increasing the missed-case penalty shifted the lowest-cost evaluated threshold downward, from 0.19 to 0.03 across the tested scenarios.
- At a fixed 20% review capacity, the existing analysis identified 2,572 positive cases and achieved 51.80% recall. A strict-capacity recalculation is required because the original rounding method selected one application beyond the 20% limit.

The findings demonstrate that screening strategies depend on both model predictions and the assumed costs of operational decisions.

## 2. Dataset and Methodology

The analysis used the existing validation partition of 61,502 applications, including 4,965 observations with recorded repayment difficulty.

The previously trained LightGBM classifier was evaluated without additional model training.

Probability thresholds ranging from 0.02 to 0.50 were evaluated in increments of 0.01.

Fixed-capacity strategies were also tested, selecting the highest-scoring applicants at review capacities between 5% and 50%.

The original held-out test dataset remained unused.

## 3. Probability Threshold Analysis

| Threshold | Flagged | Precision | Recall | False Negatives |
|---:|---:|---:|---:|---:|
| 0.05 | 32,797 | 12.61% | 83.30% | 829 |
| 0.10 | 15,745 | 18.77% | 59.54% | 2,009 |
| 0.15 | 8,590 | 24.24% | 41.93% | 2,883 |
| 0.20 | 4,982 | 28.80% | 28.90% | 3,530 |
| 0.30 | 1,664 | 37.50% | 12.57% | 4,341 |
| 0.50 | 156 | 55.13% | 1.73% | 4,879 |

Increasing the decision threshold reduced the proportion of applications flagged and increased precision, but substantially decreased recall.

At a threshold of 0.05, the model captured 83.30% of positive cases while flagging approximately 53.33% of all applications.

At a threshold of 0.20, the review rate decreased to approximately 8.10%, but recall fell to 28.90%.

This illustrates the tradeoff between screening workload and the number of positive cases missed.

## 4. Hypothetical Cost Model

The modeled cost function was:

**Total Modeled Cost = (Flagged Applications × Review Cost) + (False Negatives × Missed-Case Cost)**

The baseline scenario assumed:

- Review cost: 25 hypothetical units per flagged application.
- Missed-case cost: 500 hypothetical units per positive case left unflagged.

These values were selected for analytical demonstration and do not represent observed operational costs or credit losses.

### Lowest-Cost Threshold

Among the evaluated probability thresholds, the lowest modeled cost occurred at a threshold of **0.06**.

| Metric | Result |
|---|---:|
| Threshold | 0.06 |
| Applications Flagged | 27,951 |
| Review Rate | 45.45% |
| True Positives | 3,895 |
| False Negatives | 1,070 |
| Precision | 13.94% |
| Recall | 78.45% |
| Total Modeled Cost | 1,233,775 |

The modeled cost was calculated as:

(27,951 × 25) + (1,070 × 500) = 1,233,775 units.

The nearby threshold of 0.05 produced a modeled cost of 1,234,425 units, only 650 units higher.

This narrow difference indicates that the exact preferred threshold is sensitive to the evaluation sample and cost assumptions.

## 5. Fixed-Capacity Screening

The original fixed-capacity analysis produced the following results:

| Requested Capacity | Applicants Reviewed | Positive Cases Captured | Recall | Modeled Cost |
|---|---:|---:|---:|---:|
| 5% | 3,076 | 995 | 20.04% | 2,061,900 |
| 10% | 6,151 | 1,669 | 33.62% | 1,801,775 |
| 15% | 9,226 | 2,176 | 43.83% | 1,625,150 |
| 20% | 12,301 | 2,572 | 51.80% | 1,504,025 |
| 25% | 15,376 | 2,909 | 58.59% | 1,412,400 |
| 30% | 18,451 | 3,215 | 64.75% | 1,336,275 |
| 40% | 24,601 | 3,697 | 74.46% | 1,249,025 |
| 50% | 30,751 | 4,037 | 81.31% | 1,232,775 |

*Rounding note:* The original implementation used ceiling rounding for requested capacities, resulting in 12,301 applications at the 20% level. This exceeds exactly 20% of the validation population by one application. A revised implementation using floor rounding is required for strict-capacity analysis.

### Interpretation

Under the baseline hypothetical costs, higher review capacities generally produced lower modeled costs within the evaluated range.

At the 50% review level, the modeled cost was 1,232,775 units, the lowest among the evaluated capacity strategies.

A strict maximum capacity of 20% should be enforced using integer applicant counts. The exact corrected cost requires recalculation after excluding the additional application.

## 6. Cost Sensitivity Analysis

Four scenarios were evaluated using a constant review cost of 25 units and varying missed-case costs.

| Missed-Case Cost | Lowest-Cost Threshold | Review Rate | Recall | Modeled Cost |
|---:|---:|---:|---:|---:|
| 125 | 0.19 | 8.99% | 31.28% | 564,700 |
| 250 | 0.10 | 25.60% | 59.54% | 895,875 |
| 500 | 0.06 | 45.45% | 78.45% | 1,233,775 |
| 1,000 | 0.03 | 75.33% | 94.26% | 1,443,225 |

### Interpretation

As the assumed missed-case cost increased relative to the review cost, the lowest-cost evaluated probability threshold decreased.

When missed-case costs were low, the cost model favored reviewing a relatively small percentage of applications.

When missed-case costs were high, the model favored broader screening to capture a larger proportion of positive cases.

This demonstrates that a screening threshold cannot be chosen from model discrimination metrics alone.

## 7. Comparison With No Review

Under the baseline missed-case penalty of 500 units, a no-review strategy produces a modeled cost of:

4,965 × 500 = **2,482,500 hypothetical units**.

The original 20%-capacity scenario produced a modeled cost of 1,504,025 units, representing a modeled difference of 978,475 units.

This difference is not an estimate of real financial savings.

The cost model assumes that capturing a positive case avoids its missed-case penalty. It does not establish that a manual review would prevent an adverse outcome.

## 8. Business Interpretation

Probability thresholds and fixed-capacity rankings serve different analytical purposes.

Probability thresholds provide a consistent scoring rule but result in variable review volumes as score distributions change.

Fixed-capacity screening controls the number of reviewed applications directly, which can be useful when staffing or resources are constrained.

The sensitivity analysis demonstrates that preferences between strategies depend on the assumed costs of reviews and missed cases.

These results are appropriate for exploratory decision analytics, but they are not sufficient to justify real-world automated credit approval, denial, or adverse-action policies.

## 9. Limitations

The model was evaluated on a validation partition previously used during development.

The threshold selected from validation outcomes may be optimistic and requires independent assessment.

The hypothetical cost assumptions were not derived from observed losses, operational review expenses, or actual intervention effectiveness.

The analysis excludes revenue effects, loan profitability, customer impacts, approval outcomes, compliance requirements, and fairness evaluation.

A flagged application does not necessarily represent an avoided loss, and the cost model cannot establish causal benefits of an intervention.

The held-out test set remains reserved for final evaluation.

## 10. Next Steps — Day 11

The next phase will begin development of an interactive credit risk analytics dashboard.

The dashboard will combine:

- Model discrimination and performance comparisons.
- Risk decile distributions and observed difficulty rates.
- Cumulative capture and lift analysis.
- Interactive screening capacity and threshold exploration.
- Hypothetical cost sensitivity analysis.
- Selected aggregate feature-importance findings.

The dashboard will use aggregate evaluation tables and clearly distinguish validation-based findings from hypothetical decision scenarios.

**Tools:** Python, pandas, NumPy, LightGBM, scikit-learn, matplotlib, DuckDB.