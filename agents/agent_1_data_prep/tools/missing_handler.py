"""
Tool: Handle missing values per configuration.
"""

from __future__ import annotations

from typing import Tuple, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MissingValueHandler:
    def __init__(self, config):
        self.config = config

    def handle(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        summary: Dict[str, Any] = {}
        missing_ratio = df.isna().mean().to_dict()
        summary["missing_ratio"] = missing_ratio

        drop_cols = [
            col for col, ratio in missing_ratio.items() if ratio > self.config.drop_threshold
        ]
        if drop_cols:
            df = df.drop(columns=drop_cols)
            summary["dropped_columns"] = drop_cols

        if self.config.impute_strategy == "median":
            df = df.fillna(df.median(numeric_only=True))
        elif self.config.impute_strategy == "mean":
            df = df.fillna(df.mean(numeric_only=True))
        elif self.config.impute_strategy == "mode":
            df = df.fillna(df.mode().iloc[0])

        df = df.fillna(0)
        return df, summary

