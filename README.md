# 🔧 End-to-End ETL Pipeline — CSV/API → Transform → PostgreSQL

## Problem Statement
Data teams frequently need reliable, repeatable pipelines to ingest data from multiple sources (CSV files, REST APIs), apply business transformations and quality checks, and load clean data into a relational database for downstream analytics.

## Approach
1. **Extract** – Pull from local CSV files and a public REST API (JSONPlaceholder)
2. **Transform** – Type casting, deduplication, null handling, derived columns
3. **Validate** – Schema checks, row count assertions, null thresholds, range validation
4. **Load** – Upsert into PostgreSQL using SQLAlchemy (supports Snowflake too)
5. **Log** – Structured logging with run metadata (start time, rows processed, status)
6. **Schedule** – APScheduler cron job for automated daily runs

## Tech Stack
| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Database | PostgreSQL (SQLAlchemy ORM) |
| Data Processing | Pandas, NumPy |
| API Client | requests |
| Scheduling | APScheduler |
| Logging | Python logging + JSON handler |
| Config | python-dotenv (.env) |
| Testing | pytest |

## Project Structure
```
etl-pipeline-postgres/
├── data/
│   ├── raw/                      # Source CSV files
│   └── processed/                # Post-transform staging
├── logs/                         # Pipeline run logs (JSON)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Environment config
│   ├── extract.py                # CSV and API extraction
│   ├── transform.py              # Business transformations
│   ├── validate.py               # Data quality checks
│   ├── load.py                   # PostgreSQL loader (SQLAlchemy)
│   ├── pipeline.py               # Orchestrator — runs full ETL
│   └── scheduler.py              # APScheduler cron setup
├── tests/
│   ├── test_transform.py
│   └── test_validate.py
├── sql/
│   └── create_tables.sql         # DDL for PostgreSQL tables
├── .env.example                  # Environment variable template
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Environment
```bash
git clone https://github.com/Saideva0318/etl-pipeline-postgres.git
cd etl-pipeline-postgres
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Database
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Create Tables
```bash
psql -U your_user -d your_db -f sql/create_tables.sql
```

### 4. Run Pipeline
```bash
# One-time run
python src/pipeline.py

# Scheduled run (daily at 6 AM)
python src/scheduler.py
```

## Data Validation Rules
| Check | Rule | Action on Fail |
|-------|------|----------------|
| Schema | Required columns present | Abort pipeline |
| Nulls | < 5% null rate per column | Warning log |
| Revenue | revenue >= 0 | Drop invalid rows |
| Duplicates | Unique transaction_id | Deduplicate |
| Row count | > 0 rows loaded | Abort pipeline |

## Logging
Logs are written to `logs/etl_run_YYYYMMDD.json` and stdout.

Sample log entry:
```json
{"timestamp": "2024-01-15T06:00:01", "level": "INFO", "stage": "extract", "rows": 5000, "source": "sales_data.csv"}
{"timestamp": "2024-01-15T06:00:03", "level": "INFO", "stage": "validate", "passed": true, "checks": 5}
{"timestamp": "2024-01-15T06:00:05", "level": "INFO", "stage": "load", "rows_inserted": 4987, "table": "sales_transactions"}
```

## License
MIT
