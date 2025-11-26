"""
Typed state definition for Data Preparation workflow.
"""

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime


class DatasetArtifact(TypedDict, total=False):
    train_path: str
    val_path: Optional[str]
    test_path: str
    schema_path: Optional[str]
    qc_report_path: Optional[str]


class DataPrepState(TypedDict, total=False):
    # Session metadata
    session_id: str
    job_id: str
    user_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[float]

    # Input
    input_source: Literal["upload", "catalog", "auto"]
    source_path: Optional[str]
    catalog_id: Optional[str]
    file_format: Optional[str]
    domain: Optional[str]
    modality: Optional[str]
    difficulty: Optional[str]
    model_choice: Optional[str]

    # Data payload
    raw_data: Optional[List[Dict]]
    dataframe: Optional["pd.DataFrame"]  # type: ignore[name-defined]
    record_count: int

    # Cleaning status flags
    status: Literal[
        "pending",
        "uploading",
        "loading",
        "cleaning",
        "splitting",
        "validating",
        "completed",
        "failed",
    ]
    errors: List[str]
    warnings: List[str]

    # Metrics
    missing_value_summary: Dict[str, float]
    duplicate_summary: Dict[str, int]
    validation_results: Dict[str, Dict]

    # Output artifacts
    artifacts: DatasetArtifact
    event_payload: Dict[str, str]
    retry_count: int
    max_retries: int

