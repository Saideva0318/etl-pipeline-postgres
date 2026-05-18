"""
Pipeline Orchestrator
Runs the full ETL pipeline: Extract → Transform → Validate → Load.
"""

import logging
import json
from datetime import datetime
from pathlib import Path

from config import LOG_DIR
from extract import extract_from_csv, extract_from_api
from transform import transform_sales_data, transform_api_data
from validate import DataValidator, ValidationError
from load import load_to_postgres

# ─── Logging Setup ───────────────────────────────────────────────────────────
LOG_DIR.mkdir(exist_ok=True)
log_filename = LOG_DIR / f"etl_run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)
logger = logging.getLogger("pipeline")


def run_sales_etl() -> dict:
    """
    Full ETL run for sales transaction data.
    
    Returns:
        Run metadata dict with status, rows processed, timestamps
    """
    run_meta = {
        "pipeline": "sales_etl",
        "start_time": datetime.utcnow().isoformat(),
        "status": "RUNNING",
        "rows_extracted": 0,
        "rows_loaded": 0,
        "errors": []
    }
    
    try:
        # 1. EXTRACT
        logger.info("=" * 60)
        logger.info("PIPELINE START — sales_etl")
        logger.info("=" * 60)
        raw_df = extract_from_csv("sales_data.csv", parse_dates=["date"])
        run_meta["rows_extracted"] = len(raw_df)
        
        # 2. TRANSFORM
        transformed_df = transform_sales_data(raw_df)
        
        # 3. VALIDATE
        validator = DataValidator(transformed_df, table_name="sales_transactions")
        clean_df = (
            validator
            .check_required_columns(["transaction_id", "date", "revenue"])
            .check_row_count(min_rows=1)
            .check_null_rate("revenue", max_null_pct=5.0)
            .check_non_negative("revenue")
            .check_no_duplicates(["transaction_id"])
            .get_clean_df()
        )
        
        # 4. LOAD
        rows_loaded = load_to_postgres(clean_df, table_name="sales_transactions", if_exists="append")
        run_meta["rows_loaded"] = rows_loaded
        run_meta["status"] = "SUCCESS"
        
    except ValidationError as e:
        logger.error(f"Pipeline aborted — Validation failure: {e}")
        run_meta["status"] = "FAILED"
        run_meta["errors"].append(str(e))
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected error: {e}")
        run_meta["status"] = "FAILED"
        run_meta["errors"].append(str(e))
    finally:
        run_meta["end_time"] = datetime.utcnow().isoformat()
        logger.info(f"PIPELINE COMPLETE — Status: {run_meta['status']} | Rows: {run_meta['rows_loaded']:,}")
        logger.info("=" * 60)
    
    return run_meta


def run_api_etl() -> dict:
    """
    ETL run for API data (JSONPlaceholder /posts as demo).
    Replace with your actual API endpoint.
    """
    run_meta = {"pipeline": "api_etl", "start_time": datetime.utcnow().isoformat(), "status": "RUNNING"}
    
    try:
        raw_df = extract_from_api("https://jsonplaceholder.typicode.com/posts")
        transformed_df = transform_api_data(raw_df)
        
        validator = DataValidator(transformed_df, "api_posts")
        clean_df = (
            validator
            .check_required_columns(["post_id", "user_id", "title"])
            .check_row_count(min_rows=1)
            .get_clean_df()
        )
        
        rows_loaded = load_to_postgres(clean_df, "api_posts", if_exists="replace")
        run_meta.update({"rows_loaded": rows_loaded, "status": "SUCCESS"})
    except Exception as e:
        logger.error(f"API ETL failed: {e}")
        run_meta.update({"status": "FAILED", "error": str(e)})
    finally:
        run_meta["end_time"] = datetime.utcnow().isoformat()
    
    return run_meta


if __name__ == "__main__":
    # Run all pipelines
    results = []
    results.append(run_sales_etl())
    results.append(run_api_etl())
    
    print("\n" + "=" * 60)
    print("ETL PIPELINE RUN SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"  {r['pipeline']:20s} | Status: {r['status']:8s} | Rows: {r.get('rows_loaded', 0):,}")
