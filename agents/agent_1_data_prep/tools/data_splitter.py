"""
Tool: Split cleaned dataset and persist artifacts.
"""

from __future__ import annotations

from typing import Dict, Optional
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
import logging
import uuid

logger = logging.getLogger(__name__)


class DataSplitter:
    def __init__(self, config):
        self.config = config

    def split_and_save(
        self,
        df: pd.DataFrame,
        job_id: Optional[str],
        stratify_on: Optional[str],
    ) -> Dict[str, str]:
        job_id = job_id or uuid.uuid4().hex
        output_dir = Path(self.config.artifact_directory) / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        stratify_series = df[stratify_on] if stratify_on and stratify_on in df else None

        train_ratio = self.config.train_ratio
        temp_ratio = 1 - train_ratio

        train_df, temp_df = train_test_split(
            df,
            test_size=temp_ratio,
            stratify=stratify_series,
            random_state=self.config.random_seed,
        )

        test_ratio = self.config.test_ratio / (self.config.validation_ratio + self.config.test_ratio)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=test_ratio,
            random_state=self.config.random_seed,
        )

        train_path = output_dir / "train.csv"
        val_path = output_dir / "validation.csv"
        test_path = output_dir / "test.csv"

        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        test_df.to_csv(test_path, index=False)

        schema_path = None
        if self.config.save_schema:
            schema_path = output_dir / "schema.json"
            df.dtypes.astype(str).to_json(schema_path)

        artifacts = {
            "train_path": str(train_path),
            "val_path": str(val_path),
            "test_path": str(test_path),
            "schema_path": str(schema_path) if schema_path else None,
        }

        logger.info("Saved dataset artifacts to %s", output_dir)
        return artifacts

