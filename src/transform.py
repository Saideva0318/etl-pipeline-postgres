"""
Transform Module
Business logic transformations applied to raw extracted data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply business transformations to sales transaction data.
    
    Transformations applied:
      - Parse and standardize date column
      - Remove duplicate transaction_ids
      - Drop rows with null revenue or transaction_id
      - Clip negative revenue to 0
      - Add derived columns: year, month, quarter, profit_margin_pct
      - Add ETL metadata: etl_loaded_at timestamp
    
    Args:
        df: Raw extracted DataFrame
    
    Returns:
        Transformed DataFrame ready for loading
    """
    initial_rows = len(df)
    
    # Standardize date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    
    # Deduplication
    if "transaction_id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["transaction_id"])
        dupes_removed = before - len(df)
        if dupes_removed > 0:
            logger.warning(f"[TRANSFORM] Removed {dupes_removed} duplicate transaction_ids")
    
    # Drop nulls on critical columns
    critical_cols = [c for c in ["transaction_id", "revenue"] if c in df.columns]
    df = df.dropna(subset=critical_cols)
    
    # Clip invalid numeric values
    for col in ["revenue", "cost", "quantity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)
    
    # Derived time features
    if "date" in df.columns:
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.quarter
    
    # Derived business metrics
    if "revenue" in df.columns and "cost" in df.columns:
        df["profit"] = (df["revenue"] - df["cost"]).round(2)
        df["profit_margin_pct"] = np.where(
            df["revenue"] > 0,
            (df["profit"] / df["revenue"] * 100).round(2),
            0.0
        )
    
    # ETL metadata
    df["etl_loaded_at"] = datetime.utcnow().isoformat()
    
    final_rows = len(df)
    logger.info(f"[TRANSFORM] {initial_rows:,} rows in → {final_rows:,} rows out ({initial_rows - final_rows} dropped)")
    return df.reset_index(drop=True)


def transform_api_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data fetched from a REST API (JSONPlaceholder /posts endpoint).
    Renames columns, adds metadata, drops unnecessary fields.
    """
    df = df.rename(columns={"id": "post_id", "userId": "user_id", "title": "title", "body": "content"})
    df["title"] = df["title"].str.title().str.strip()
    df["content"] = df["content"].str.replace("\n", " ").str.strip()
    df["etl_loaded_at"] = datetime.utcnow().isoformat()
    logger.info(f"[TRANSFORM] API data transformed: {len(df):,} records")
    return df
