""
Tool: Remove duplicate records.
""

from __future__ import annotations

from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DuplicateRemover:
    def __init__(self, config):
        self.config = config

    def remove(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        summary: Dict[str, Any] = {}

        key_cols: Optional[List[str]] = self.config.duplicate_key_columns
        before = len(df)

        if key_cols:
            df = df.drop_duplicates(subset=key_cols)
            summary["key_columns"] = key_cols
        else:
            df = df.drop_duplicates()

        removed = before - len(df)
        summary["rows_removed"] = removed

        if removed:
            logger.info("Removed %s duplicate rows", removed)

        return df, summary

