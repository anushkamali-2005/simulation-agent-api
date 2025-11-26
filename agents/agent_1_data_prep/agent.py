"""
Agent 1: Data Preparation Agent
Orchestrates ingestion, cleaning, validation, and dataset packaging.
"""

from typing import Dict, Any
import logging
from langgraph.graph import StateGraph

from .config import DataPrepConfig, DEFAULT_CONFIG
from .graph.state import DataPrepState
from .graph.workflow import create_data_prep_workflow
from .tools.dataset_selector import DatasetSelector
from .tools.data_loader import DataLoader
from .tools.data_cleaner import DataCleaner
from .tools.missing_handler import MissingValueHandler
from .tools.duplicate_remover import DuplicateRemover
from .tools.data_splitter import DataSplitter
from .tools.data_validator import DataValidator
from .tools.file_uploader import FileUploader

logger = logging.getLogger(__name__)


class DataPreparationAgent:
    """Top-level coordinator for Agent 1."""

    def __init__(self, config: DataPrepConfig = DEFAULT_CONFIG):
        self.config = config
        self.agent_name = "DataPreparationAgent"

        # Tools
        self.dataset_selector = DatasetSelector(config)
        self.file_uploader = FileUploader(config)
        self.data_loader = DataLoader(config)
        self.missing_handler = MissingValueHandler(config)
        self.data_cleaner = DataCleaner(config)
        self.duplicate_remover = DuplicateRemover(config)
        self.data_splitter = DataSplitter(config)
        self.data_validator = DataValidator(config)

        # Workflow graph
        self.graph: StateGraph | None = None
        self.compiled_graph = None

        logger.info("%s initialized", self.agent_name)

    def create_graph(self) -> StateGraph:
        return create_data_prep_workflow(
            dataset_selector=self.dataset_selector,
            file_uploader=self.file_uploader,
            data_loader=self.data_loader,
            missing_handler=self.missing_handler,
            data_cleaner=self.data_cleaner,
            duplicate_remover=self.duplicate_remover,
            data_splitter=self.data_splitter,
            data_validator=self.data_validator,
            config=self.config,
        )

    def compile_graph(self) -> None:
        if self.graph is None:
            self.graph = self.create_graph()
        self.compiled_graph = self.graph.compile()
        logger.info("%s workflow compiled", self.agent_name)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if self.compiled_graph is None:
            self.compile_graph()

        logger.info("Starting %s run", self.agent_name)
        try:
            final_state = await self.compiled_graph.ainvoke(state)
            logger.info(
                "%s completed. Records: %s, Status: %s",
                self.agent_name,
                final_state.get("record_count"),
                final_state.get("status"),
            )
            return final_state
        except Exception as exc:
            logger.exception("%s failed: %s", self.agent_name, exc)
            state.setdefault("errors", []).append(str(exc))
            state["status"] = "failed"
            raise

    async def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        return await self.execute(initial_state)

    def get_state_schema(self) -> type:
        return DataPrepState

