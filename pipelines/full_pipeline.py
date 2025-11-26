"""
End-to-end automation orchestrator that chains Agent 1 (data prep),
Vertex AI training (placeholder), and Agent 2 (simulation testing).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging
import uuid

from agents.agent_1_data_prep.agent import DataPreparationAgent
from agents.agent_1_data_prep.config import DataPrepConfig
from agents.agent_2_simulation.agent import SimulationTestingAgent

logger = logging.getLogger(__name__)


@dataclass
class TrainingResult:
    model_path: str
    model_name: str
    training_job_id: str
    metrics: Dict[str, float]


class VertexTrainingManager:
    """
    Placeholder for submitting fine-tuning jobs to Vertex AI (or any backend).
    Replace the body of submit_training_job with real API calls.
    """

    def __init__(self, default_bucket: str = "gs://medagent-models"):
        self.default_bucket = default_bucket

    async def submit_training_job(
        self,
        dataset_artifacts: Dict[str, str],
        model_choice: str,
        tuning_strategy: Optional[str] = None,
    ) -> TrainingResult:
        training_job_id = f"train-{uuid.uuid4().hex[:8]}"
        model_path = f"{self.default_bucket}/{model_choice}/{training_job_id}/model.ckpt"

        logger.info(
            "Submitting training job %s for model=%s artifacts=%s strategy=%s",
            training_job_id,
            model_choice,
            dataset_artifacts,
            tuning_strategy,
        )

        # TODO: integrate with Vertex AI SDK. For now, simulate async wait.
        await asyncio.sleep(0.1)

        metrics = {"training_accuracy": 0.90, "loss": 0.2}
        return TrainingResult(
            model_path=model_path,
            model_name=model_choice,
            training_job_id=training_job_id,
            metrics=metrics,
        )


class FullWorkflowOrchestrator:
    """
    Coordinates user intent -> data prep -> training -> simulation.
    Retries with adjusted strategy if simulation accuracy < threshold.
    """

    def __init__(
        self,
        data_agent: Optional[DataPreparationAgent] = None,
        simulation_agent: Optional[SimulationTestingAgent] = None,
        training_manager: Optional[VertexTrainingManager] = None,
        max_iterations: int = 3,
    ):
        self.data_agent = data_agent or DataPreparationAgent(DataPrepConfig())
        self.simulation_agent = simulation_agent or SimulationTestingAgent()
        self.training_manager = training_manager or VertexTrainingManager()
        self.max_iterations = max_iterations

    async def run(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        retry_count = 0
        last_simulation_state: Dict[str, Any] = {}

        while retry_count < self.max_iterations:
            logger.info("Starting iteration %s/%s", retry_count + 1, self.max_iterations)

            data_state = await self.data_agent.run(
                {
                    "session_id": user_request.get("session_id", uuid.uuid4().hex),
                    "job_id": uuid.uuid4().hex,
                    "domain": user_request.get("domain"),
                    "modality": user_request.get("modality"),
                    "difficulty": user_request.get("difficulty"),
                    "model_choice": user_request.get("model_choice"),
                    "input_source": "auto",
                    "emit_event": False,
                    "retry_count": retry_count,
                    "max_retries": self.max_iterations,
                }
            )

            training_result = await self.training_manager.submit_training_job(
                dataset_artifacts=data_state.get("artifacts", {}),
                model_choice=data_state.get("model_choice"),
                tuning_strategy=user_request.get("tuning_strategy"),
            )

            sim_state = {
                "session_id": data_state["session_id"],
                "job_id": data_state["job_id"],
                "timestamp": data_state.get("created_at"),
                "model_path": training_result.model_path,
                "model_name": training_result.model_name,
                "model_type": training_result.model_name,
                "simulation_questions": [],
                "model_answers": [],
                "benchmark_answers": [],
                "num_questions": user_request.get("num_questions", 50),
                "difficulty": user_request.get("difficulty", "varied"),
                "domains": [data_state.get("domain")] if data_state.get("domain") else None,
                "errors": [],
                "warnings": [],
                "retry_count": retry_count,
                "max_retries": self.max_iterations,
            }

            last_simulation_state = await self.simulation_agent.run(sim_state)

            if last_simulation_state.get("simulation_passed"):
                logger.info("Model passed simulation accuracy threshold.")
                return {
                    "status": "passed",
                    "data_state": data_state,
                    "training_result": training_result,
                    "simulation_state": last_simulation_state,
                    "iterations": retry_count + 1,
                }

            logger.warning(
                "Simulation failed (accuracy=%s). Preparing for retry.",
                last_simulation_state.get("simulation_accuracy"),
            )

            retry_count += 1
            user_request["tuning_strategy"] = self._choose_next_strategy(
                last_simulation_state, retry_count
            )

        return {
            "status": "failed",
            "simulation_state": last_simulation_state,
            "iterations": retry_count,
        }

    @staticmethod
    def _choose_next_strategy(sim_state: Dict[str, Any], retry_count: int) -> str:
        if sim_state.get("error_types", {}).get("safety_concern"):
            return "safety_focus"
        if sim_state.get("simulation_accuracy", 0) < 0.7:
            return "increase_data"
        return f"tuning_round_{retry_count}"


async def main():
    orchestrator = FullWorkflowOrchestrator()
    user_request = {
        "session_id": "demo-session",
        "domain": "cardiology",
        "modality": "ehr",
        "model_choice": "MedLM",
        "num_questions": 50,
    }
    result = await orchestrator.run(user_request)
    logger.info("Pipeline result: %s", result["status"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

