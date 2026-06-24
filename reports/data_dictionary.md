# Data Dictionary — Bluestock Mutual Fund Analytics

## Table: dim_fund
| Column | Type | Definition | Source |
|---|---|---|---|
| fund_id | INTEGER | Primary key | Generated |
| amfi_code | INTEGER | Unique AMFI scheme code | fund_master.csv |
| scheme_name | TEXT | Full name of the mutual fund scheme | fund_master.csv |
| fund_house | TEXT | AMC name (e.g. HDFC, SBI) | fund_master.csv |
| category | TEXT | Fund category (Equity/Debt/Hybrid) | fund_master.csv |
| sub_category | TEXT | Sub-category (Large Cap, Mid Cap etc.) | fund_master.csv |
| risk_grade | TEXT | Risk level (Low/Moderate/High) | fund_master.csv |

## Table: dim_date
| Column | Type | Definition | Source |
|---|---|---|---|
| date_id | INTEGER | Primary key | Generated |
| full_date | DATE | Full calendar date | Generated |
| day | INTEGER | Day of month (1–31) | Generated |
| month | INTEGER | Month number (1–12) | Generated |
| year | INTEGER | Calendar year | Generated |
| quarter | INTEGER | Quarter (1–4) | Generated |
| is_weekend | INTEGER | 1 if Saturday/Sunday, else 0 | Generated |

## Table: fact_nav
| Column | Type | Definition | Source |
|---|---|---|---|
| nav_id | INTEGER | Primary key | Generated |
| amfi_code | INTEGER | Foreign key → dim_fund | nav_history.csv |
| date_id | INTEGER | Foreign key → dim_date | nav_history.csv |
| nav_value | REAL | Net Asset Value in INR | nav_history.csv |

## Table: fact_transactions
| Column | Type | Definition | Source |
|---|---|---|---|
| txn_id | INTEGER | Primary key | Generated |
| investor_id | TEXT | Unique investor identifier | investor_transactions.csv |
| amfi_code | INTEGER | Foreign key → dim_fund | investor_transactions.csv |
| date_id | INTEGER | Foreign key → dim_date | investor_transactions.csv |
| transaction_type | TEXT | SIP / Lumpsum / Redemption | investor_transactions.csv |
| amount | REAL | Transaction amount in INR | investor_transactions.csv |
| units | REAL | Number of units bought/sold | investor_transactions.csv |
| state | TEXT | Indian state of investor | investor_transactions.csv |
| kyc_status | TEXT | KYC verification status | investor_transactions.csv |

## Table: fact_performance
| Column | Type | Definition | Source |
|---|---|---|---|
| perf_id | INTEGER | Primary key | Generated |
| amfi_code | INTEGER | Foreign key → dim_fund | scheme_performance.csv |
| date_id | INTEGER | Foreign key → dim_date | scheme_performance.csv |
| return_1yr | REAL | 1 year return percentage | scheme_performance.csv |
| return_3yr | REAL | 3 year CAGR percentage | scheme_performance.csv |
| return_5yr | REAL | 5 year CAGR percentage | scheme_performance.csv |
| expense_ratio | REAL | Annual expense ratio % (0.1–2.5) | scheme_performance.csv |
| sharpe_ratio | REAL | Risk adjusted return metric | scheme_performance.csv |

## Table: fact_aum
| Column | Type | Definition | Source |
|---|---|---|---|
| aum_id | INTEGER | Primary key | Generated |
| amfi_code | INTEGER | Foreign key → dim_fund | aum_data.csv |
| date_id | INTEGER | Foreign key → dim_date | aum_data.csv |
| aum_crores | REAL | Assets Under Management in INR crores | aum_data.csv |