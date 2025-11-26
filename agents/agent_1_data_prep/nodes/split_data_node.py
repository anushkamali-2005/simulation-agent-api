"""
Node: Split cleaned data into train/val/test.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def split_data_node(state: Dict[str, Any], data_splitter) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("NODE: Split Data")
    logger.info("=" * 60)

    try:
        df = state.get("dataframe")
        if df is None:
            raise ValueError("No dataframe present for splitting")

        state["status"] = "splitting"

        split_artifacts = data_splitter.split_and_save(
            df=df,
            job_id=state.get("job_id"),
            stratify_on=state.get("stratify_on"),
        )

        state["artifacts"] = split_artifacts
        logger.info("✅ Data splitting complete. %s", split_artifacts)

    except Exception as exc:
        logger.exception("❌ Splitting failed: %s", exc)
        state.setdefault("errors", []).append(f"Split error: {exc}")
        state["status"] = "failed"
        raise

    return state

