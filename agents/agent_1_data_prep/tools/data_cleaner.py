"""
Tool: Perform domain-aware cleaning (normalization, encoding).
"""

from __future__ import annotations

from typing import Tuple, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    def __init__(self, config):
        self.config = config

    def clean(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        summary: Dict[str, Any] = {}

        if self.config.normalize_numeric:
            numeric_cols = df.select_dtypes(include="number").columns
            summary["normalized_columns"] = list(numeric_cols)
            df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / (
                df[numeric_cols].std().replace(0, 1)
            )

        if self.config.encode_categorical:
            cat_cols = df.select_dtypes(include="object").columns
            df = pd.get_dummies(df, columns=cat_cols, dummy_na=True)
            summary["encoded_columns"] = list(cat_cols)

        return df, summary

