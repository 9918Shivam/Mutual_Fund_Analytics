-- ============================================
-- BLUESTOCK MF — 10 ANALYTICAL SQL QUERIES
-- ============================================

-- Q1: Top 5 funds by AUM
SELECT
    f.scheme_name,
    f.fund_house,
    SUM(a.aum_crores) AS total_aum
FROM fact_aum a
JOIN dim_fund f ON a.amfi_code = f.amfi_code
GROUP BY f.amfi_code
ORDER BY total_aum DESC
LIMIT 5;

-- Q2: Average NAV per month for each fund
SELECT
    f.scheme_name,
    d.year,
    d.month,
    ROUND(AVG(n.nav_value), 2) AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date_id = d.date_id
GROUP BY f.amfi_code, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month;

-- Q3: SIP transaction YoY growth
SELECT
    d.year,
    COUNT(*) AS sip_count,
    ROUND(SUM(t.amount), 2) AS total_sip_amount
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;

-- Q4: Total transactions by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- Q5: Funds with expense ratio less than 1%
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- Q6: Best performing funds by 3 year return
SELECT
    f.scheme_name,
    f.category,
    ROUND(AVG(p.return_3yr), 2) AS avg_3yr_return
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.amfi_code
ORDER BY avg_3yr_return DESC
LIMIT 10;

-- Q7: Monthly SIP vs Lumpsum vs Redemption comparison
SELECT
    d.year,
    d.month,
    transaction_type,
    COUNT(*) AS count,
    ROUND(SUM(amount), 2) AS total_amount
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
GROUP BY d.year, d.month, transaction_type
ORDER BY d.year, d.month;

-- Q8: Funds with highest Sharpe ratio (best risk-adjusted return)
SELECT
    f.scheme_name,
    f.risk_grade,
    ROUND(AVG(p.sharpe_ratio), 3) AS avg_sharpe
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.amfi_code
ORDER BY avg_sharpe DESC
LIMIT 5;

-- Q9: KYC status breakdown of investors
SELECT
    kyc_status,
    COUNT(*) AS investor_count,
    ROUND(SUM(amount), 2) AS total_invested
FROM fact_transactions
GROUP BY kyc_status;

-- Q10: Category wise average expense ratio
SELECT
    f.category,
    ROUND(AVG(p.expense_ratio), 3) AS avg_expense_ratio,
    COUNT(DISTINCT f.amfi_code) AS fund_count
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY avg_expense_ratio;