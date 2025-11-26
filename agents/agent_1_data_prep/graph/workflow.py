"""
LangGraph workflow definition for Data Preparation Agent.
"""

from langgraph.graph import StateGraph, END
import logging

from .state import DataPrepState
from ..nodes.select_dataset_node import select_dataset_node
from ..nodes.load_data_node import load_data_node
from ..nodes.clean_data_node import clean_data_node
from ..nodes.split_data_node import split_data_node
from ..nodes.validate_data_node import validate_data_node

logger = logging.getLogger(__name__)


def create_data_prep_workflow(
    dataset_selector,
    file_uploader,
    data_loader,
    missing_handler,
    data_cleaner,
    duplicate_remover,
    data_splitter,
    data_validator,
    config=None,
) -> StateGraph:
    """
    Build the directed workflow for Agent 1.
    """
    logger.info("Building data-prep workflow")

    workflow = StateGraph(DataPrepState)

    workflow.add_node(
        "select_dataset",
        lambda state: select_dataset_node(state, dataset_selector, config),
    )

    workflow.add_node(
        "load_data",
        lambda state: load_data_node(state, file_uploader, data_loader),
    )

    workflow.add_node(
        "clean_data",
        lambda state: clean_data_node(
            state,
            missing_handler,
            data_cleaner,
            duplicate_remover,
        ),
    )

    workflow.add_node(
        "split_data",
        lambda state: split_data_node(state, data_splitter),
    )

    workflow.add_node(
        "validate_data",
        lambda state: validate_data_node(state, data_validator),
    )

    workflow.set_entry_point("select_dataset")
    workflow.add_edge("select_dataset", "load_data")
    workflow.add_edge("load_data", "clean_data")
    workflow.add_edge("clean_data", "split_data")
    workflow.add_edge("split_data", "validate_data")
    workflow.add_edge("validate_data", END)

    logger.info("Data-prep workflow ready")
    return workflow

