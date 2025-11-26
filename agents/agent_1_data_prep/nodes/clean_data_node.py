"""
Node: Clean and preprocess dataset.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def clean_data_node(
    state: Dict[str, Any],
    missing_handler,
    data_cleaner,
    duplicate_remover,
) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("NODE: Clean Data")
    logger.info("=" * 60)

    try:
        df = state.get("dataframe")
        if df is None:
            raise ValueError("No dataframe present in state")

        state["status"] = "cleaning"

        df, missing_summary = missing_handler.handle(df)
        df, cleaning_summary = data_cleaner.clean(df)
        df, duplicate_summary = duplicate_remover.remove(df)

        state["dataframe"] = df
        state["missing_value_summary"] = missing_summary
        state["cleaning_summary"] = cleaning_summary
        state["duplicate_summary"] = duplicate_summary

        logger.info(
            "✅ Cleaning complete. Rows: %s, Columns: %s",
            df.shape[0],
            df.shape[1],
        )

    except Exception as exc:
        logger.exception("❌ Cleaning failed: %s", exc)
        state.setdefault("errors", []).append(f"Cleaning error: {exc}")
        state["status"] = "failed"
        raise

    return state

