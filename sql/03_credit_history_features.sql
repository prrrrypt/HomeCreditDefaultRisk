
-- Day 4: Applicant-Level Credit History Feature Engineering
-- Source: Home Credit Default Risk / bureau.csv
-- Grain: One row per SK_ID_CURR

CREATE OR REPLACE VIEW bureau_features AS
WITH bureau_aggregated AS (
    SELECT
        SK_ID_CURR,

        -- Credit account activity
        COUNT(*) AS bureau_total_accounts,

        COUNT(*) FILTER (
            WHERE CREDIT_ACTIVE = 'Active'
        ) AS bureau_active_accounts,

        COUNT(*) FILTER (
            WHERE CREDIT_ACTIVE = 'Closed'
        ) AS bureau_closed_accounts,

        -- Credit exposure and balances
        SUM(AMT_CREDIT_SUM) AS bureau_total_credit,

        SUM(AMT_CREDIT_SUM_DEBT) AS bureau_total_debt,

        SUM(AMT_CREDIT_SUM_OVERDUE) AS bureau_total_overdue,

        MAX(AMT_CREDIT_SUM) AS bureau_max_credit,

        -- Historical delinquency
        MAX(CREDIT_DAY_OVERDUE) AS bureau_max_days_overdue,

        COUNT(*) FILTER (
            WHERE CREDIT_DAY_OVERDUE > 0
        ) AS bureau_accounts_currently_overdue,

        -- Historical credit recency
        AVG(-DAYS_CREDIT) AS bureau_avg_days_since_credit,

        MIN(-DAYS_CREDIT) AS bureau_days_since_recent_credit,

        MAX(-DAYS_CREDIT) AS bureau_days_since_oldest_credit,

        -- Data coverage
        COUNT(AMT_CREDIT_SUM_DEBT) AS bureau_debt_records_available,

        COUNT(AMT_CREDIT_SUM) AS bureau_credit_records_available

    FROM bureau
    GROUP BY SK_ID_CURR
)

SELECT
    *,
    bureau_total_debt /
        NULLIF(bureau_total_credit, 0)
        AS bureau_debt_credit_ratio

FROM bureau_aggregated;


-- Join historical credit features to applications
-- Preserve exactly one row per application

CREATE OR REPLACE VIEW modeling_features AS
SELECT
    a.*,

    -- Additional application-level financial features
    a.AMT_CREDIT /
        NULLIF(a.AMT_INCOME_TOTAL, 0)
        AS credit_income_ratio,

    a.AMT_ANNUITY /
        NULLIF(a.AMT_INCOME_TOTAL, 0)
        AS annuity_income_ratio,

    -a.DAYS_BIRTH / 365.25
        AS age_years,

    CASE
        WHEN a.DAYS_EMPLOYED = 365243 THEN NULL
        ELSE -a.DAYS_EMPLOYED / 365.25
    END AS employment_years,

    CASE
        WHEN a.DAYS_EMPLOYED = 365243 THEN 1
        ELSE 0
    END AS employment_sentinel_flag,

    -- Distinguish no recorded bureau history
    -- from bureau accounts with missing financial values
    CASE
        WHEN b.SK_ID_CURR IS NULL THEN 0
        ELSE 1
    END AS has_bureau_history,

    b.* EXCLUDE (SK_ID_CURR)

FROM applications a
LEFT JOIN bureau_features b
    ON a.SK_ID_CURR = b.SK_ID_CURR;
