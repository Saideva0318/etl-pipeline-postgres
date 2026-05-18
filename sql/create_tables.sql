-- DDL: Create tables for ETL pipeline output
-- Run: psql -U your_user -d your_db -f sql/create_tables.sql

CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id      VARCHAR(20) PRIMARY KEY,
    date                TIMESTAMP NOT NULL,
    product             VARCHAR(100),
    region              VARCHAR(50),
    quantity            INTEGER,
    unit_price          NUMERIC(10, 2),
    revenue             NUMERIC(12, 2) NOT NULL CHECK (revenue >= 0),
    cost                NUMERIC(12, 2),
    profit              NUMERIC(12, 2),
    profit_margin_pct   NUMERIC(6, 2),
    year                INTEGER,
    month               INTEGER,
    quarter             INTEGER,
    etl_loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_posts (
    post_id             INTEGER PRIMARY KEY,
    user_id             INTEGER,
    title               VARCHAR(500),
    content             TEXT,
    etl_loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id              SERIAL PRIMARY KEY,
    pipeline_name       VARCHAR(100),
    start_time          TIMESTAMP,
    end_time            TIMESTAMP,
    rows_extracted      INTEGER,
    rows_loaded         INTEGER,
    status              VARCHAR(20),
    error_message       TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_transactions(date);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales_transactions(region);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_transactions(product);
