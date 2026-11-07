-- Query 1: Credit-to-Income Ratio and Payment Difficulty
WITH borrower_ratios AS (
    SELECT
        SK_ID_CURR,
        TARGET,
        AMT_CREDIT / NULLIF(AMT_INCOME_TOTAL, 0)
            AS credit_income_ratio
    FROM applications
    WHERE AMT_INCOME_TOTAL > 0
),
segmented AS (
    SELECT
        *,
        NTILE(5) OVER (
            ORDER BY credit_income_ratio
        ) AS risk_quintile
    FROM borrower_ratios
)
SELECT
    risk_quintile,
    COUNT(*) AS applicants,
    ROUND(AVG(credit_income_ratio), 2)
        AS avg_credit_income_ratio,
    ROUND(100.0 * AVG(TARGET), 2)
        AS difficulty_rate_pct
FROM segmented
GROUP BY risk_quintile
ORDER BY risk_quintile;

-- Query 2: Income Quintiles and Payment Difficulty
WITH income_groups AS (
    SELECT
        TARGET,
        AMT_CREDIT,
        AMT_INCOME_TOTAL,
        NTILE(5) OVER (
            ORDER BY AMT_INCOME_TOTAL
        ) AS income_quintile
    FROM applications
    WHERE AMT_INCOME_TOTAL > 0
)
SELECT
    income_quintile,
    COUNT(*) AS applicants,
    ROUND(AVG(AMT_INCOME_TOTAL), 2)
        AS avg_income,
    ROUND(AVG(AMT_CREDIT), 2)
        AS avg_credit,
    ROUND(100.0 * AVG(TARGET), 2)
        AS difficulty_rate_pct
FROM income_groups
GROUP BY income_quintile
ORDER BY income_quintile;

-- Query 3: Annuity-to-Income Ratio and Payment Difficulty
WITH payment_ratios AS (
    SELECT
        TARGET,
        AMT_ANNUITY / NULLIF(AMT_INCOME_TOTAL, 0)
            AS annuity_income_ratio
    FROM applications
    WHERE AMT_INCOME_TOTAL > 0
      AND AMT_ANNUITY IS NOT NULL
),
segmented AS (
    SELECT
        *,
        NTILE(5) OVER (
            ORDER BY annuity_income_ratio
        ) AS payment_quintile
    FROM payment_ratios
)
SELECT
    payment_quintile,
    COUNT(*) AS applicants,
    ROUND(AVG(annuity_income_ratio), 3)
        AS avg_annuity_income_ratio,
    ROUND(100.0 * AVG(TARGET), 2)
        AS difficulty_rate_pct
FROM segmented
GROUP BY payment_quintile
ORDER BY payment_quintile;

-- Query 4: Employment Duration and Payment Difficulty
WITH employment_groups AS (
    SELECT
        TARGET,
        CASE
            WHEN DAYS_EMPLOYED = 365243 THEN 'Sentinel value'
            WHEN DAYS_EMPLOYED IS NULL THEN 'Missing'
            WHEN DAYS_EMPLOYED > 0 THEN 'Other positive'
            WHEN -DAYS_EMPLOYED / 365.25 < 1 THEN '<1 year'
            WHEN -DAYS_EMPLOYED / 365.25 < 3 THEN '1-3 years'
            WHEN -DAYS_EMPLOYED / 365.25 < 5 THEN '3-5 years'
            WHEN -DAYS_EMPLOYED / 365.25 < 10 THEN '5-10 years'
            ELSE '10+ years'
        END AS employment_group
    FROM applications
)
SELECT
    employment_group,
    COUNT(*) AS applicants,
    ROUND(100.0 * AVG(TARGET), 2)
        AS difficulty_rate_pct
FROM employment_groups
GROUP BY employment_group
ORDER BY
    CASE employment_group
        WHEN '<1 year' THEN 1
        WHEN '1-3 years' THEN 2
        WHEN '3-5 years' THEN 3
        WHEN '5-10 years' THEN 4
        WHEN '10+ years' THEN 5
        ELSE 8
    END;