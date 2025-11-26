"""
Node: Load raw data into memory / dataframe.
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def load_data_node(state: Dict[str, Any], file_uploader, data_loader) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("NODE: Load Data")
    logger.info("=" * 60)

    try:
        state["status"] = "loading"
        source = state.get("input_source", "upload")

        if source == "upload" and state.get("uploaded_file"):
            logger.info("Processing uploaded file: %s", state["uploaded_file"])
            source_path = file_uploader.save_upload(state["uploaded_file"])
        else:
            catalog_id = state.get("catalog_id")
            logger.info("Using catalog dataset: %s", catalog_id)
            source_path = data_loader.resolve_catalog_path(catalog_id)

        dataframe = data_loader.load(source_path, fmt=state.get("file_format"))
        record_count = len(dataframe)

        state["source_path"] = source_path
        state["dataframe"] = dataframe
        state["record_count"] = record_count
        state.setdefault("created_at", datetime.utcnow())
        state.setdefault("errors", [])
        state.setdefault("warnings", [])

        logger.info("✅ Loaded %s records from %s", record_count, source_path)

    except Exception as exc:
        logger.exception("❌ Data loading failed: %s", exc)
        state.setdefault("errors", []).append(f"Load error: {exc}")
        state["status"] = "failed"
        raise

    return state

