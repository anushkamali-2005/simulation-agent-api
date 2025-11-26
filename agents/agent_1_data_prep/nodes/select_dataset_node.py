"""
Node: Interpret user intent and select dataset/model defaults.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def select_dataset_node(state: Dict[str, Any], dataset_selector, config) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("NODE: Select Dataset & Model")
    logger.info("=" * 60)

    try:
        state.setdefault("status", "pending")
        domain = state.get("domain") or "general_medicine"
        modality = state.get("modality")
        difficulty = state.get("difficulty")

        selection = dataset_selector.select(domain, modality, difficulty)
        state["catalog_id"] = selection["catalog_id"]
        state["input_source"] = selection.get("source", "catalog")
        state.setdefault("selection_notes", selection.get("description"))

        model_choice = state.get("model_choice") or config.default_model
        if model_choice not in config.supported_models:
            logger.warning(
                "Model %s not supported. Falling back to %s",
                model_choice,
                config.default_model,
            )
            model_choice = config.default_model
        state["model_choice"] = model_choice

        logger.info(
            "✅ Selected dataset=%s model=%s for domain=%s",
            state["catalog_id"],
            state["model_choice"],
            domain,
        )

    except Exception as exc:
        logger.exception("❌ Dataset selection failed: %s", exc)
        state.setdefault("errors", []).append(f"Dataset selection error: {exc}")
        state["status"] = "failed"
        raise

    return state

