"""
Unit Tests — Validate Module
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validate import DataValidator, ValidationError


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "transaction_id": [f"TXN_{i}" for i in range(100)],
        "revenue": [float(i * 10) for i in range(100)],
        "date": pd.date_range("2023-01-01", periods=100)
    })


def test_required_columns_pass(clean_df):
    v = DataValidator(clean_df)
    v.check_required_columns(["transaction_id", "revenue"])  # should not raise


def test_required_columns_fail(clean_df):
    v = DataValidator(clean_df)
    with pytest.raises(ValidationError):
        v.check_required_columns(["transaction_id", "missing_column"])


def test_row_count_pass(clean_df):
    v = DataValidator(clean_df)
    v.check_row_count(min_rows=10)  # should not raise


def test_row_count_fail():
    empty_df = pd.DataFrame(columns=["transaction_id", "revenue"])
    v = DataValidator(empty_df)
    with pytest.raises(ValidationError):
        v.check_row_count(min_rows=1)


def test_non_negative_drops_rows(clean_df):
    clean_df.loc[0, "revenue"] = -50.0
    v = DataValidator(clean_df)
    v.check_non_negative("revenue")
    result = v.get_clean_df()
    assert (result["revenue"] >= 0).all()
