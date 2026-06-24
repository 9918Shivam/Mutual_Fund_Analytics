-- ============================================
-- BLUESTOCK MUTUAL FUND STAR SCHEMA
-- ============================================

-- DIMENSION: Fund details
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_id         INTEGER PRIMARY KEY,
    amfi_code       INTEGER UNIQUE NOT NULL,
    scheme_name     TEXT NOT NULL,
    fund_house      TEXT,
    category        TEXT,
    sub_category    TEXT,
    risk_grade      TEXT
);

-- DIMENSION: Date details
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         INTEGER PRIMARY KEY,
    full_date       DATE UNIQUE NOT NULL,
    day             INTEGER,
    month           INTEGER,
    year            INTEGER,
    quarter         INTEGER,
    is_weekend      INTEGER  -- 0 or 1
);

-- FACT: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER,
    date_id         INTEGER,
    nav_value       REAL NOT NULL,
    FOREIGN KEY (amfi_code)  REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)    REFERENCES dim_date(date_id)
);

-- FACT: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    amfi_code           INTEGER,
    date_id             INTEGER,
    transaction_type    TEXT CHECK(transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount              REAL CHECK(amount > 0),
    units               REAL,
    state               TEXT,
    kyc_status          TEXT CHECK(kyc_status IN ('Verified','Pending','Rejected')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

-- FACT: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER,
    date_id         INTEGER,
    return_1yr      REAL,
    return_3yr      REAL,
    return_5yr      REAL,
    expense_ratio   REAL CHECK(expense_ratio BETWEEN 0.1 AND 2.5),
    sharpe_ratio    REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

-- FACT: AUM (Assets Under Management)
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER,
    date_id         INTEGER,
    aum_crores      REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);