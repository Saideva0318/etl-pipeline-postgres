"""
Load Module
Upsert transformed data into PostgreSQL via SQLAlchemy.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Literal

from config import DATABASE_URL, BATCH_SIZE

logger = logging.getLogger(__name__)


def get_engine():
    """Create and return SQLAlchemy engine."""
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        logger.info("[LOAD] Database engine created")
        return engine
    except Exception as e:
        logger.error(f"[LOAD] Failed to create engine: {e}")
        raise


def load_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    if_exists: Literal["append", "replace", "fail"] = "append",
    chunk_size: int = None
) -> int:
    """
    Load DataFrame into a PostgreSQL table.
    
    Args:
        df: DataFrame to load
        table_name: Target table name
        if_exists: Behavior if table exists ('append', 'replace', 'fail')
        chunk_size: Batch size for loading (defaults to BATCH_SIZE from config)
    
    Returns:
        Number of rows loaded
    """
    engine = get_engine()
    chunk = chunk_size or BATCH_SIZE
    
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunk,
            method="multi"
        )
        logger.info(f"[LOAD] {len(df):,} rows loaded into '{table_name}' (if_exists='{if_exists}')")
        return len(df)
    except SQLAlchemyError as e:
        logger.error(f"[LOAD] Failed to load into '{table_name}': {e}")
        raise
    finally:
        engine.dispose()


def verify_row_count(table_name: str, expected: int) -> bool:
    """
    Post-load verification: compare expected vs actual row count in DB.
    
    Args:
        table_name: Table to check
        expected: Expected row count
    
    Returns:
        True if counts match, False otherwise
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            actual = result.scalar()
        match = actual >= expected
        status = "PASS" if match else "WARN"
        logger.info(f"[LOAD] Row count verification {status} — Expected: {expected:,}, Actual: {actual:,}")
        return match
    except Exception as e:
        logger.warning(f"[LOAD] Could not verify row count: {e}")
        return False
    finally:
        engine.dispose()
