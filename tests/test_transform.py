"""
Unit Tests — Transform Module
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transform import transform_sales_data, transform_api_data


@pytest.fixture
def raw_sales_df():
    """Sample raw sales data with known issues."""
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({
        "transaction_id": [f"TXN_{i:03d}" for i in range(10)],
        "date": dates,
        "product": ["Widget A"] * 10,
        "region": ["North"] * 10,
        "quantity": list(range(1, 11)),
        "unit_price": [10.0] * 10,
        "revenue": [10.0 * i for i in range(1, 11)],
        "cost": [5.0 * i for i in range(1, 11)]
    })
    # Inject duplicate
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    return df


def test_transform_removes_duplicates(raw_sales_df):
    result = transform_sales_data(raw_sales_df)
    assert result["transaction_id"].duplicated().sum() == 0


def test_transform_adds_derived_columns(raw_sales_df):
    result = transform_sales_data(raw_sales_df)
    for col in ["year", "month", "quarter", "profit", "profit_margin_pct", "etl_loaded_at"]:
        assert col in result.columns


def test_transform_no_negative_revenue(raw_sales_df):
    raw_sales_df.loc[0, "revenue"] = -100.0
    result = transform_sales_data(raw_sales_df)
    assert (result["revenue"] >= 0).all()


def test_transform_api_data():
    raw = pd.DataFrame([{"id": 1, "userId": 1, "title": "hello world", "body": "test body"}])
    result = transform_api_data(raw)
    assert "post_id" in result.columns
    assert "etl_loaded_at" in result.columns
