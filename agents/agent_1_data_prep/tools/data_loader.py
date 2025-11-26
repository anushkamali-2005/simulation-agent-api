"""
Tool: Load raw datasets from uploads or catalog storage.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, config):
        self.config = config

    def resolve_catalog_path(self, catalog_id: Optional[str]) -> str:
        if not catalog_id:
            raise ValueError("catalog_id is required for catalog source")
        catalog_dir = Path("catalogs") / catalog_id
        if not catalog_dir.exists():
            raise FileNotFoundError(f"Catalog dataset {catalog_id} not found")
        candidates = list(catalog_dir.glob("*.*"))
        if not candidates:
            raise FileNotFoundError(f"No files found for catalog {catalog_id}")
        return str(candidates[0])

    def load(self, path: str, fmt: Optional[str] = None) -> pd.DataFrame:
        fmt = fmt or Path(path).suffix.replace(".", "").lower()
        logger.info("Loading dataset (%s): %s", fmt, path)

        if fmt == "csv":
            return pd.read_csv(path)
        if fmt in ("json", "jsonl"):
            return pd.read_json(path, lines=fmt == "jsonl")
        if fmt in ("parquet", "pq"):
            return pd.read_parquet(path)

        raise ValueError(f"Unsupported file format: {fmt}")

