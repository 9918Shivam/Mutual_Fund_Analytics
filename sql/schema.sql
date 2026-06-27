-- ============================================
-- BLUESTOCK MUTUAL FUND — STAR SCHEMA
-- ============================================

-- DIMENSION: Fund details
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER UNIQUE NOT NULL,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    launch_date         TEXT
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date   DATE UNIQUE NOT NULL,
    day         INTEGER,
    month       INTEGER,
    year        INTEGER,
    quarter     INTEGER,
    is_weekend  INTEGER
);

-- FACT: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER,
    date        TEXT,
    nav         REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    transaction_date    TEXT,
    amfi_code           INTEGER,
    transaction_type    TEXT CHECK(transaction_type IN ('SIP','LUMPSUM','REDEMPTION')),
    amount_inr          REAL CHECK(amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER,
    scheme_name         TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL CHECK(expense_ratio_pct BETWEEN 0.1 AND 2.5),
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT,
    fund_house      TEXT,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER
);