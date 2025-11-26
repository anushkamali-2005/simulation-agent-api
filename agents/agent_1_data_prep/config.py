"""
Configuration for Agent 1: Data Preparation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class DataPrepConfig:
    """Configurable knobs for the data preparation pipeline."""

    # Input handling
    supported_formats: List[str] = field(
        default_factory=lambda: ["csv", "json", "parquet"]
    )
    upload_directory: str = "storage/uploads"
    staging_directory: str = "storage/staging"
    dataset_metadata_path: str = "agents/agent_1_data_prep/data/metadata.json"

    # Cleaning rules
    drop_threshold: float = 0.6  # drop columns with >60% missing
    impute_strategy: str = "median"  # median / mean / mode
    normalize_numeric: bool = True
    encode_categorical: bool = True

    # Duplicate detection
    duplicate_key_columns: Optional[List[str]] = None
    fuzzy_match: bool = True

    # Splitting
    train_ratio: float = 0.8
    validation_ratio: float = 0.1
    test_ratio: float = 0.1
    stratify_on: Optional[str] = "label"
    random_seed: int = 42

    # Output + logging
    artifact_directory: str = "storage/processed"
    save_schema: bool = True
    generate_qc_report: bool = True

    # Integration
    notify_simulation_agent: bool = True
    event_topic: str = "dataset_ready"

    # Model selection defaults
    supported_models: List[str] = field(
        default_factory=lambda: ["MedLM", "T5Gemma", "Custom"]
    )
    default_model: str = "MedLM"


DEFAULT_CONFIG = DataPrepConfig()

