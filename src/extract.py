"""
Extract Module
Pull data from CSV files and REST APIs.
"""

import pandas as pd
import requests
from pathlib import Path
from typing import Optional
import logging

from config import RAW_DATA_PATH

logger = logging.getLogger(__name__)


def extract_from_csv(filename: str, parse_dates: Optional[list] = None) -> pd.DataFrame:
    """
    Extract data from a CSV file in the raw data directory.
    
    Args:
        filename: CSV filename (relative to raw data path)
        parse_dates: List of columns to parse as dates
    
    Returns:
        DataFrame with extracted data
    """
    filepath = RAW_DATA_PATH / filename
    if not filepath.exists():
        logger.warning(f"File not found: {filepath} — generating mock data")
        return _generate_mock_csv_data(filepath)
    
    df = pd.read_csv(filepath, parse_dates=parse_dates or [])
    logger.info(f"[EXTRACT] CSV: {filename} — {len(df):,} rows loaded")
    return df


def extract_from_api(url: str, params: dict = None, data_key: str = None) -> pd.DataFrame:
    """
    Extract data from a REST API endpoint.
    
    Args:
        url: API endpoint URL
        params: Optional query parameters
        data_key: JSON key that contains the list of records (None = root is list)
    
    Returns:
        DataFrame with extracted data
    """
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        records = data[data_key] if data_key else data
        df = pd.DataFrame(records)
        logger.info(f"[EXTRACT] API: {url} — {len(df):,} records fetched")
        return df
    except requests.exceptions.RequestException as e:
        logger.error(f"[EXTRACT] API call failed: {e}")
        raise


def _generate_mock_csv_data(filepath: Path) -> pd.DataFrame:
    """Generate and save mock sales CSV data for demo purposes."""
    import numpy as np
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    np.random.seed(42)
    n = 5000
    dates = pd.date_range("2023-01-01", periods=n, freq="H")
    df = pd.DataFrame({
        "transaction_id": [f"TXN_{i:06d}" for i in range(1, n + 1)],
        "date": dates,
        "product": np.random.choice(["Widget A", "Widget B", "Widget C", "Widget D"], n),
        "region": np.random.choice(["North", "South", "East", "West"], n),
        "quantity": np.random.randint(1, 20, n),
        "unit_price": np.random.uniform(10, 200, n).round(2),
        "revenue": np.random.uniform(50, 4000, n).round(2),
        "cost": np.random.uniform(20, 2000, n).round(2)
    })
    df["profit"] = (df["revenue"] - df["cost"]).round(2)
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.info(f"[EXTRACT] Mock CSV generated and saved to {filepath}")
    return df
