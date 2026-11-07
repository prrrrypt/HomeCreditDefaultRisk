-- Query 1: Overall Payment Difficulty Rate
SELECT
    TARGET,
    COUNT(*) AS application_count,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM applications
GROUP BY TARGET
ORDER BY TARGET;

-- Query 2: Income Type and Payment Difficulty
SELECT
    NAME_INCOME_TYPE,
    COUNT(*) AS total_applicants,
    SUM(TARGET) AS difficulty_cases,
    ROUND(
        100.0 * AVG(TARGET),
        2
    ) AS difficulty_rate_pct
FROM applications
GROUP BY NAME_INCOME_TYPE
ORDER BY difficulty_rate_pct DESC;

-- Query 3: Credit-to-Income Ratio
WITH loan_ratios AS (
    SELECT
        SK_ID_CURR,
        TARGET,
        AMT_CREDIT / NULLIF(AMT_INCOME_TOTAL, 0)
            AS credit_to_income_ratio
    FROM applications
    WHERE AMT_INCOME_TOTAL > 0
),
risk_groups AS (
    SELECT
        TARGET,
        CASE
            WHEN credit_to_income_ratio < 1 THEN 'Under 1'
            WHEN credit_to_income_ratio < 2 THEN '1 to 2'
            WHEN credit_to_income_ratio < 3 THEN '2 to 3'
            WHEN credit_to_income_ratio < 5 THEN '3 to 5'
            ELSE '5 or more'
        END AS ratio_group
    FROM loan_ratios
)
SELECT
    ratio_group,
    COUNT(*) AS applicants,
    ROUND(
        100.0 * AVG(TARGET),
        2
    ) AS difficulty_rate_pct
FROM risk_groups
GROUP BY ratio_group
ORDER BY
    CASE ratio_group
        WHEN 'Under 1' THEN 1
        WHEN '1 to 2' THEN 2
        WHEN '2 to 3' THEN 3
        WHEN '3 to 5' THEN 4
        ELSE 5
    END;

-- Query 4: Age and Payment Difficulty
WITH applicant_ages AS (
    SELECT
        TARGET,
        FLOOR(-DAYS_BIRTH / 365.25) AS age
    FROM applications
)
SELECT
    CASE
        WHEN age < 30 THEN 'Under 30'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        WHEN age < 60 THEN '50-59'
        ELSE '60+'
    END AS age_group,
    COUNT(*) AS applicants,
    ROUND(
        100.0 * AVG(TARGET),
        2
    ) AS difficulty_rate_pct
FROM applicant_ages
GROUP BY age_group
ORDER BY 
    CASE age_group
        WHEN 'Under 30' THEN 1
        WHEN '30-39' THEN 2
        WHEN '40-49' THEN 3
        WHEN '50-59' THEN 4
        ELSE 5
    END;