# End-to-End ETL Pipeline — CSV/API → Transform → PostgreSQL

![CI](https://github.com/Saideva0318/etl-pipeline-postgres/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

> **Production-grade, containerized ETL pipeline** that extracts data from CSV files and REST APIs, applies business transformations with data validation, and loads clean records into PostgreSQL using SQLAlchemy — with APScheduler for automated daily runs, structured logging, and Docker support.

---

## Business Problem

Data engineering teams need reliable, observable, and repeatable pipelines that move raw data from operational sources into analytics-ready databases without data loss or silent failures. This project demonstrates a complete ETL architecture with validation gates, logging, and scheduling — deployable via Docker in under 5 minutes.

---

## Pipeline Architecture

```
+===========================================+
|         ETL PIPELINE ARCHITECTURE        |
+===========================================+

  [CSV Files]         [REST API]
       |                   |
       +--------+----------+
                |
                v
  +-------------+-------------+
  |      EXTRACT Layer        |
  |  csv_extractor.py         |
  |  api_extractor.py         |
  |  - schema detection       |
  |  - encoding handling      |
  +-------------+-------------+
                |
                v
  +-------------+-------------+
  |    TRANSFORM Layer        |
  |  transformer.py           |
  |  - type casting           |
  |  - deduplication          |
  |  - derived columns        |
  |  - null handling          |
  |  - ETL timestamp          |
  +-------------+-------------+
                |
                v
  +-------------+-------------+
  |    VALIDATE Layer         |
  |  validator.py             |
  |  - schema checks          |
  |  - row count assertions   |
  |  - null thresholds        |
  |  - range validation       |
  |  - CRITICAL vs WARNING    |
  +-------------+-------------+
                |
                v
  +-------------+-------------+
  |      LOAD Layer           |
  |  loader.py                |
  |  - SQLAlchemy upsert      |
  |  - batched insert         |
  |  - post-load verification |
  |  - PostgreSQL / Snowflake |
  +-------------+-------------+
                |
      +---------+---------+
      |                   |
      v                   v
  [PostgreSQL DB]   [Logs + Reports]
  etl_db schema     logs/etl_YYYYMMDD.log

  Scheduler: APScheduler CRON (daily @ 6 AM ET)
  Container: Docker + docker-compose
```

---

## Key Features

- **Multi-Source Extraction** — CSV files + REST API (JSONPlaceholder) with schema detection
- **Data Validation Engine** — `DataValidator` class with CRITICAL/WARNING severity levels
- **Batched Upsert Loading** — SQLAlchemy ORM with post-load row count verification
- **Structured Logging** — Rotating JSON logs with run metadata, timing, and row counts
- **APScheduler Scheduling** — Configurable cron (default: 6 AM daily, Eastern time)
- **Docker Support** — Multi-stage Dockerfile + docker-compose with health checks
- **PostgreSQL + Snowflake ready** — SQLAlchemy dialect-agnostic loader
- **Unit Tested** — pytest suite with real PostgreSQL service in CI

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|----------|
| Language | Python 3.10+ | Core pipeline logic |
| Database | PostgreSQL 15 | Target analytics DB |
| ORM | SQLAlchemy 2.x | DB-agnostic upsert loading |
| Data Processing | Pandas, NumPy | Transform & validation |
| API Client | requests | REST API extraction |
| Scheduling | APScheduler | Cron-based pipeline runs |
| Config | python-dotenv | Environment management |
| Logging | Python logging | Structured rotating logs |
| Testing | pytest, pytest-cov | Unit tests + coverage |
| Containerization | Docker, docker-compose | Reproducible deployment |
| CI/CD | GitHub Actions | Lint, test, Docker build |

---

## Project Structure

```
etl-pipeline-postgres/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI: lint + test + Docker build
├── data/
│   ├── raw/                    # Source CSV files
│   └── processed/              # Post-transform staging
├── logs/                       # Pipeline run logs (JSON)
├── sql/
│   └── create_tables.sql       # DDL with indexes + constraints
├── src/
│   ├── __init__.py
│   ├── extractor.py            # CSV + API extraction
├──   ├── transformer.py          # Data transformation engine
│   ├── validator.py            # Data quality validation
│   ├── loader.py               # SQLAlchemy upsert to PostgreSQL
│   └── pipeline.py             # Orchestrator + APScheduler
├── tests/
│   ├── test_extractor.py
│   ├── test_transformer.py
│   ├── test_validator.py
│   └── test_loader.py
├── .env.example                # Environment variable template
├── .gitignore
├── Dockerfile                  # Multi-stage production build
├── docker-compose.yml          # PostgreSQL + ETL + pgAdmin
├── README.md
└── requirements.txt
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and configure
git clone https://github.com/Saideva0318/etl-pipeline-postgres.git
cd etl-pipeline-postgres
cp .env.example .env

# 2. Start all services (PostgreSQL + ETL)
docker-compose up --build

# 3. Optional: Launch pgAdmin UI
docker-compose --profile dev up
# Visit http://localhost:5050
```

### Option 2: Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in DB credentials
python -m src.pipeline
```

---

## Environment Variables

```bash
# .env.example
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=etl_db
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=your_secure_password
LOG_LEVEL=INFO
SCHEDULE_CRON=0 6 * * *   # Daily at 6 AM
```

---

## Data Validation Rules

| Check | Severity | Description |
|-------|----------|-------------|
| Schema validation | CRITICAL | All required columns present |
| Row count | CRITICAL | Min 1 row after transform |
| Null threshold | WARNING | <5% nulls in key columns |
| Negative values | WARNING | Revenue/quantity >= 0 |
| Duplicate check | WARNING | No duplicate primary keys |
| Post-load count | CRITICAL | Loaded rows match expected |

---

## Running Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Skills Demonstrated

`Python` `PostgreSQL` `SQLAlchemy` `ETL Pipeline` `Data Engineering` `Docker` `docker-compose` `APScheduler` `Data Validation` `Pandas` `GitHub Actions` `CI/CD` `pytest` `Logging` `REST API` `Data Quality`

---

## Author

**Saideva** — Data Engineer & Analytics Professional | [GitHub](https://github.com/Saideva0318) | [LinkedIn](https://linkedin.com/in/saideva)

---

*Built with production-quality code standards — clean, tested, Dockerized, and interview-ready.*
