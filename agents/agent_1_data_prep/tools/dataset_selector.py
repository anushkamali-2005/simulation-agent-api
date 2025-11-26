"""
Tool: Select appropriate dataset based on user intent (domain, modality).
"""

from __future__ import annotations

from typing import Dict, List, Optional
import json
from pathlib import Path
import logging
import random

logger = logging.getLogger(__name__)


class DatasetSelector:
    def __init__(self, config):
        self.config = config
        self.metadata_path = Path(self.config.dataset_metadata_path)
        if not self.metadata_path.exists():
            logger.warning(
                "Dataset metadata file not found at %s. Selection will fallback.",
                self.metadata_path,
            )
            self.metadata: Dict[str, Dict] = {}
        else:
            with open(self.metadata_path, "r", encoding="utf-8") as fp:
                self.metadata = json.load(fp)

    def select(
        self,
        domain: str,
        modality: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Choose dataset info for requested domain/modality.
        Returns dict with catalog_id and justification.
        """
        if not self.metadata:
            raise FileNotFoundError("Dataset metadata is empty; cannot select dataset.")

        candidates: List[Dict] = []
        for dataset_id, info in self.metadata.items():
            if domain and domain not in info.get("domains", []):
                continue
            if modality and modality not in info.get("modalities", []):
                continue
            candidates.append({"dataset_id": dataset_id, **info})

        if not candidates:
            logger.warning(
                "No dataset matched domain=%s modality=%s. Falling back to any dataset.",
                domain,
                modality,
            )
            for dataset_id, info in self.metadata.items():
                candidates.append({"dataset_id": dataset_id, **info})

        choice = random.choice(candidates)

        logger.info(
            "Selected dataset %s for domain=%s modality=%s difficulty=%s",
            choice["dataset_id"],
            domain,
            modality,
            difficulty,
        )

        return {
            "catalog_id": choice["dataset_id"],
            "description": choice.get("description", ""),
            "source": choice.get("source", "catalog"),
        }

