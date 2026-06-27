-- ============================================
-- BLUESTOCK MF — 10 ANALYTICAL SQL QUERIES
-- ============================================

-- Q1: Top 5 funds by AUM
SELECT
    fund_house,
    SUM(aum_crore) AS total_aum_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month per fund
SELECT
    amfi_code,
    STRFTIME('%Y-%m', date) AS month,
    ROUND(AVG(nav), 2)      AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month;

-- Q3: SIP inflow YoY growth
SELECT
    STRFTIME('%Y', month) AS year,
    SUM(sip_inflow_crore) AS total_sip_crore
FROM monthly_sip_inflows
GROUP BY year
ORDER BY year;

-- Q4: Total transactions by state
SELECT
    state,
    COUNT(*)              AS txn_count,
    SUM(amount_inr)       AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Q5: Funds with expense ratio less than 1%
SELECT
    scheme_name,
    expense_ratio_pct,
    risk_grade
FROM fact_performance
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Top 10 funds by 3 year return
SELECT
    scheme_name,
    fund_house,
    return_3yr_pct
FROM fact_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- Q7: Transactions split by type and gender
SELECT
    transaction_type,
    gender,
    COUNT(*)        AS count,
    SUM(amount_inr) AS total_inr
FROM fact_transactions
GROUP BY transaction_type, gender
ORDER BY transaction_type, total_inr DESC;

-- Q8: Top 5 funds by Sharpe ratio
SELECT
    scheme_name,
    risk_grade,
    ROUND(sharpe_ratio, 3) AS sharpe_ratio
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 5;

-- Q9: KYC status breakdown
SELECT
    kyc_status,
    COUNT(*)        AS investor_count,
    SUM(amount_inr) AS total_invested_inr
FROM fact_transactions
GROUP BY kyc_status;

-- Q10: Average returns by fund category
SELECT
    p.risk_grade,
    ROUND(AVG(p.return_1yr_pct), 2) AS avg_1yr,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_3yr,
    ROUND(AVG(p.return_5yr_pct), 2) AS avg_5yr,
    COUNT(*)                         AS fund_count
FROM fact_performance p
GROUP BY p.risk_grade
ORDER BY avg_3yr DESC;