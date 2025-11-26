"""
Conditional helpers for Agent 1 workflow.
"""

from typing import Dict, Literal


def should_recover_upload(state: Dict) -> Literal["retry", "fail", "next"]:
    """Decide what to do after upload step."""
    if state.get("upload_retries", 0) < 2 and state.get("upload_failed"):
        return "retry"
    if state.get("upload_failed"):
        return "fail"
    return "next"


def should_run_validation(state: Dict) -> bool:
    """Skip validation if explicitly disabled."""
    return state.get("run_validation", True)


def should_emit_event(state: Dict) -> bool:
    """Emit dataset-ready event when configured."""
    return state.get("emit_event", True)

