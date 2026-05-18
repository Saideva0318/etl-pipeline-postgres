"""Apache Airflow DAG — ETL Pipeline Orchestration

Orchestrates the full extract → validate → transform → load pipeline
on a daily schedule with retry logic and Slack alerting hooks.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# ---------------------------------------------------------------------------
# Default arguments — applied to all tasks
# ---------------------------------------------------------------------------
default_args = {
    "owner": "saideva",
    "depends_on_past": False,
    "email": ["saideva@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
}

# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id="etl_pipeline_postgres",
    default_args=default_args,
    description="Daily ETL: CSV/API → validate → transform → PostgreSQL",
    schedule_interval="0 6 * * *",   # 06:00 UTC every day
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "postgres", "data-engineering"],
    doc_md=__doc__,
) as dag:

    # ------------------------------------------------------------------
    # Task 1: Health-check — ensure DB is reachable
    # ------------------------------------------------------------------
    health_check = BashOperator(
        task_id="health_check",
        bash_command="pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER",
    )

    # ------------------------------------------------------------------
    # Task 2: Extract — pull data from CSV + REST API sources
    # ------------------------------------------------------------------
    def _extract(**context):
        from src.extractor import run_extraction
        records = run_extraction()
        context["ti"].xcom_push(key="record_count", value=len(records))
        print(f"[EXTRACT] Pulled {len(records):,} records")

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=_extract,
    )

    # ------------------------------------------------------------------
    # Task 3: Validate — enforce schema + data-quality rules
    # ------------------------------------------------------------------
    def _validate(**context):
        from src.validator import run_validation
        result = run_validation()
        if not result["passed"]:
            raise ValueError(f"Validation failed: {result['errors']}")
        print(f"[VALIDATE] {result['passed_rows']:,} rows passed, "
              f"{result['failed_rows']} rows rejected")

    validate_task = PythonOperator(
        task_id="validate",
        python_callable=_validate,
    )

    # ------------------------------------------------------------------
    # Task 4: Transform — clean, enrich, deduplicate
    # ------------------------------------------------------------------
    def _transform(**context):
        from src.transformer import run_transformation
        run_transformation()
        print("[TRANSFORM] Transformation complete")

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=_transform,
    )

    # ------------------------------------------------------------------
    # Task 5: Load — upsert into PostgreSQL
    # ------------------------------------------------------------------
    def _load(**context):
        from src.loader import run_load
        stats = run_load()
        print(f"[LOAD] Inserted: {stats['inserted']:,}, "
              f"Updated: {stats['updated']:,}, "
              f"Skipped: {stats['skipped']:,}")

    load_task = PythonOperator(
        task_id="load",
        python_callable=_load,
    )

    # ------------------------------------------------------------------
    # Task 6: Quality report — row counts + null checks post-load
    # ------------------------------------------------------------------
    quality_report = BashOperator(
        task_id="quality_report",
        bash_command="python src/quality_report.py --run-date {{ ds }}",
    )

    # ------------------------------------------------------------------
    # Pipeline dependency chain
    # ------------------------------------------------------------------
    health_check >> extract_task >> validate_task >> transform_task >> load_task >> quality_report
