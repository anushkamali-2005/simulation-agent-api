"""
Node: Validate split datasets and produce QC report.
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_data_node(state: Dict[str, Any], data_validator) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("NODE: Validate Data")
    logger.info("=" * 60)

    try:
        state["status"] = "validating"
        artifacts = state.get("artifacts")
        if not artifacts:
            raise ValueError("Missing artifacts to validate")

        validation_results = data_validator.validate(artifacts)
        qc_report_path = data_validator.generate_report(
            results=validation_results,
            job_id=state.get("job_id"),
        )

        artifacts["qc_report_path"] = qc_report_path
        state["validation_results"] = validation_results
        state["status"] = "completed"
        state["completed_at"] = datetime.utcnow()

        logger.info("✅ Validation done. QC report: %s", qc_report_path)

    except Exception as exc:
        logger.exception("❌ Validation failed: %s", exc)
        state.setdefault("errors", []).append(f"Validation error: {exc}")
        state["status"] = "failed"
        raise

    return state

