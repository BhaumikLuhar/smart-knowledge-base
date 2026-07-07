import uuid
import asyncio
import json

from evaluation.runner import run_evaluation
from evaluation.schemas import EvaluationReport

from storage.sql.sql_store import SQLStore

from core.retrieval.retrieval_pipeline import RetrievalPipeline


class EvaluationService:
    """
    Service responsible for executing and
    persisting evaluation benchmark results.
    """

    #
    # Keeps the latest evaluation report
    # in memory for fast retrieval.
    #
    _running_task: asyncio.Task | None = None
    _job_status: str = "idle"
    _job_id: str | None = None
    _latest_report: EvaluationReport | None = None

    def __init__(
        self,
        sql_store: SQLStore,
    ):
        self.sql_store = sql_store
        self.pipeline = RetrievalPipeline(
            sql_store=sql_store
        )


    def start_job(self) -> str:
        """
        Start a new evaluation if one is not already running.
        """

        if (
            self.__class__._running_task
            and not self.__class__._running_task.done()
        ):
            raise RuntimeError(
                "Evaluation already running."
            )

        self.__class__._job_id = str(
            uuid.uuid4()
        )

        self.__class__._job_status = "running"

        self.__class__._running_task = asyncio.create_task(
            self.run()
        )

        return self.__class__._job_id


    async def run(
        self,
    ) -> EvaluationReport:

        try:

            report = await run_evaluation(
                sql_store=self.sql_store,
                pipeline=self.pipeline,
            )

            self.__class__._latest_report = report

            await self.sql_store.save(
                "audit_logs",
                {
                    "user_id": None,
                    "action": "evaluation_run",
                    "resource_type": "evaluation",
                    "resource_id": self.__class__._job_id,
                    "details": {
                        "report": report.model_dump(mode="json"),
                        "dataset_version": 1,
                        "questions": report.total_questions,
                    },
                },
            )

            self.__class__._job_status = "completed"

            return report

        except Exception:

            self.__class__._job_status = "failed"

            raise

    def get_status(self):

        return {
            "job_id": self.__class__._job_id,
            "status": self.__class__._job_status,
        }    

    async def get_latest_report(
        self,
    ) -> EvaluationReport | None:
        """
        Return the latest completed evaluation.
        """

        rows = await self.sql_store.execute_raw(
            """
            SELECT details
            FROM audit_logs
            WHERE action = 'evaluation_run'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )

        if not rows:
            return None

        details = rows[0]["details"]

        #
        # asyncpg may return JSONB as string.
        #
        if isinstance(details, str):
            details = json.loads(details)

        #
        # New audit format
        #
        if "report" in details:
            details = details["report"]

        return EvaluationReport.model_validate(
            details
        )