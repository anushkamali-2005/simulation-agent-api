"""
Tool: Validate dataset artifacts and write QC report.
"""

from __future__ import annotations

from typing import Dict, Any
import pandas as pd
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    def __init__(self, config):
        self.config = config

    def validate(self, artifacts: Dict[str, str]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        for split_name, path in artifacts.items():
            if not path or not path.endswith(".csv"):
                continue
            df = pd.read_csv(path)
            results[split_name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "missing_ratio": df.isna().mean().to_dict(),
            }

        return results

    def generate_report(self, results: Dict[str, Any], job_id: str | None) -> str:
        job_id = job_id or "adhoc"
        report_dir = Path(self.config.artifact_directory) / job_id
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / "qc_report.json"
        with open(report_path, "w", encoding="utf-8") as fp:
            json.dump(results, fp, indent=2)

        logger.info("QC report saved to %s", report_path)
        return str(report_path)

