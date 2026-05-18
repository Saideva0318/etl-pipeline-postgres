"""
Validation Module
Data quality checks before loading to database.
"""

import pandas as pd
from typing import List
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when a critical data quality check fails."""
    pass


class DataValidator:
    """
    Runs a suite of data quality checks on a DataFrame.
    
    Distinguishes between:
    - CRITICAL checks: abort pipeline on failure
    - WARNING checks: log and continue
    """
    
    def __init__(self, df: pd.DataFrame, table_name: str = "unknown"):
        self.df = df
        self.table_name = table_name
        self.results = []
    
    def check_required_columns(self, required: List[str]) -> "DataValidator":
        """CRITICAL: Abort if any required column is missing."""
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            msg = f"[VALIDATE] CRITICAL — Missing columns: {missing}"
            logger.error(msg)
            raise ValidationError(msg)
        logger.info(f"[VALIDATE] Required columns check PASSED ({len(required)} columns present)")
        self.results.append({"check": "required_columns", "status": "PASS"})
        return self
    
    def check_row_count(self, min_rows: int = 1) -> "DataValidator":
        """CRITICAL: Abort if DataFrame has fewer rows than minimum."""
        if len(self.df) < min_rows:
            msg = f"[VALIDATE] CRITICAL — Row count {len(self.df)} < minimum {min_rows}"
            logger.error(msg)
            raise ValidationError(msg)
        logger.info(f"[VALIDATE] Row count check PASSED ({len(self.df):,} rows ≥ {min_rows})")
        self.results.append({"check": "row_count", "status": "PASS", "rows": len(self.df)})
        return self
    
    def check_null_rate(self, column: str, max_null_pct: float = 5.0) -> "DataValidator":
        """WARNING: Log if null rate exceeds threshold (does not abort)."""
        null_pct = self.df[column].isnull().mean() * 100
        if null_pct > max_null_pct:
            logger.warning(f"[VALIDATE] WARNING — {column}: {null_pct:.1f}% nulls (threshold: {max_null_pct}%)")
            self.results.append({"check": f"null_rate_{column}", "status": "WARN", "null_pct": round(null_pct, 2)})
        else:
            logger.info(f"[VALIDATE] Null rate check PASSED — {column}: {null_pct:.1f}%")
            self.results.append({"check": f"null_rate_{column}", "status": "PASS", "null_pct": round(null_pct, 2)})
        return self
    
    def check_non_negative(self, column: str) -> "DataValidator":
        """WARNING: Log count of negative values and drop them."""
        if column not in self.df.columns:
            return self
        neg_count = (self.df[column] < 0).sum()
        if neg_count > 0:
            logger.warning(f"[VALIDATE] WARNING — {column}: {neg_count} negative values found and will be dropped")
            self.df = self.df[self.df[column] >= 0]
            self.results.append({"check": f"non_negative_{column}", "status": "WARN", "dropped": int(neg_count)})
        else:
            logger.info(f"[VALIDATE] Non-negative check PASSED — {column}")
            self.results.append({"check": f"non_negative_{column}", "status": "PASS"})
        return self
    
    def check_no_duplicates(self, subset: List[str]) -> "DataValidator":
        """WARNING: Log duplicate count (deduplication already done in transform)."""
        dupe_count = self.df.duplicated(subset=subset).sum()
        if dupe_count > 0:
            logger.warning(f"[VALIDATE] WARNING — {dupe_count} duplicates found on {subset}")
            self.results.append({"check": "duplicates", "status": "WARN", "count": int(dupe_count)})
        else:
            logger.info(f"[VALIDATE] Duplicate check PASSED on {subset}")
            self.results.append({"check": "duplicates", "status": "PASS"})
        return self
    
    def get_clean_df(self) -> pd.DataFrame:
        """Return the (possibly modified) validated DataFrame."""
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        logger.info(f"[VALIDATE] Summary — {passed} PASS | {warned} WARN | Total rows: {len(self.df):,}")
        return self.df
