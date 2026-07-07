import json
import time
import uuid
from pathlib import Path
from datetime import datetime

from agents.workflow import run_agent_pipeline

from core.auth.user_context import UserContext
from core.retrieval.retrieval_pipeline import RetrievalPipeline

from storage.sql.sql_store import SQLStore

from evaluation.metrics import EvaluationMetrics
from evaluation.schemas import (
    EvaluationDatasetItem,
    EvaluationQuestionResult,
    EvaluationReport,
)

import logging

logger = logging.getLogger(__name__)

class EvaluationRunner:
    """
    Executes the complete evaluation benchmark.
    """

    _dataset_cache: list[EvaluationDatasetItem] | None = None

    _latest_report: EvaluationReport | None = None

    def __init__(
        self,
        sql_store: SQLStore,
        pipeline: RetrievalPipeline,
    ):
        self.sql_store = sql_store
        self.pipeline = pipeline


    def load_dataset(
        self,
    ) -> list[EvaluationDatasetItem]:
        """
        Load the benchmark dataset once.
        """

        if self.__class__._dataset_cache is not None:
            return self.__class__._dataset_cache

        dataset_path = (
            Path(__file__).parent
            / "dataset.json"
        )

        with open(
            dataset_path,
            "r",
            encoding="utf-8",
        ) as f:

            raw = json.load(f)

        dataset = [
            EvaluationDatasetItem(**item)
            for item in raw
        ]

        self.__class__._dataset_cache = dataset

        return dataset
    


    async def get_user_context(
        self,
        department_name: str,
    ) -> UserContext:
        """
        Return one active employee from the
        requested department.
        """

        sql = """
        SELECT
            u.id,
            u.email,
            u.role,
            u.department_id,
            u.is_active
        FROM users u
        JOIN departments d
            ON d.id = u.department_id
        WHERE
            d.name = $1
            AND u.is_active = TRUE
        ORDER BY
            CASE
                WHEN u.role='employee'
                THEN 0
                ELSE 1
            END
        LIMIT 1;
        """

        rows = await self.sql_store.execute_raw(
            sql,
            (department_name,),
        )

        if not rows:
            raise ValueError(
                f"No active user found for "
                f"department '{department_name}'."
            )

        row = rows[0]

        return UserContext(
            id=str(row["id"]),
            email=row["email"],
            role=row["role"],
            department_id=str(
                row["department_id"]
            ),
            is_active=row["is_active"],
        )
    

    async def evaluate_question(
        self,
        item: EvaluationDatasetItem,
    ) -> EvaluationQuestionResult:
        
        user = await self.get_user_context(
            item.evaluation_department
        )


        started = time.perf_counter()

        state = await run_agent_pipeline(
            query=item.question,
            user_context=user,
            session_id=str(uuid.uuid4()),
            pipeline=self.pipeline,
        )

        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000


        retrieval_precision = (
            EvaluationMetrics.retrieval_precision(
                state["retrieved_chunks"],
                item.expected_source_doc,
            )
        )

        citation_correctness = (
            EvaluationMetrics.citation_correctness(
                state["citations"],
                item.expected_source_doc,
            )
        )

        answer_quality = (
            EvaluationMetrics.answer_quality(
                state["answer"],
                item.expected_keywords,
            )
        )
        #
        # Temporary.
        #
        # For adversarial evaluations the dataset will
        # later provide separate user_department and
        # question_department values.
        #
        permission_leakage = (
            EvaluationMetrics.permission_leakage(
                retrieved_chunks=state[
                    "retrieved_chunks"
                ],
                answer=state["answer"],
                user_department=item.evaluation_department,
                question_department=item.department_scope,
            )
        )


        return EvaluationQuestionResult(
            question=item.question,
            department_scope=item.department_scope,
            adversarial=item.adversarial,
            answer=state["answer"],
            expected_document=item.expected_source_doc,
            retrieved_documents=sorted(
                {
                    chunk["document_name"]
                    for chunk in state["retrieved_chunks"]
                }
            ),
            cited_documents=sorted(
                {
                    citation.document_name
                    for citation in state["citations"]
                }
            ),
            retrieval_precision=retrieval_precision,
            citation_correctness=citation_correctness,
            answer_quality=answer_quality,
            permission_leakage=permission_leakage,
            latency_ms=latency_ms,
            confidence_score=state[
                "confidence_score"
            ],
            confidence_level=state[
                "confidence_level"
            ],
        )
    


    async def run(
        self,
    ) -> EvaluationReport:
        """
        Execute the complete evaluation benchmark.

        Flow
        ----
        1. Load benchmark dataset.
        2. Execute every benchmark question.
        3. Aggregate evaluation metrics.
        4. Return a typed evaluation report.
        """

        dataset = self.load_dataset()

        results: list[EvaluationQuestionResult] = []

        for item in dataset:

            try:

                result = await self.evaluate_question(
                    item
                )

                results.append(result)

            except Exception as exc:

                logger.exception(
                    "Evaluation failed for question '%s'",
                    item.question,
                )

                print(exc)

                continue

        #
        # No dataset loaded.
        #
        if not results:

            return EvaluationReport(
                retrieval_precision=0.0,
                citation_correctness=0.0,
                answer_quality=0.0,
                permission_leakage_count=0,
                latency_p95=0.0,
                total_questions=0,
                completed_at=datetime.now(),
                results_per_question=[],
            )

        retrieval_precision = (
            sum(
                r.retrieval_precision
                for r in results
            )
            / len(results)
        )

        citation_correctness = (
            sum(
                r.citation_correctness
                for r in results
            )
            / len(results)
        )

        answer_quality = (
            sum(
                r.answer_quality
                for r in results
            )
            / len(results)
        )

        permission_leakage_count = sum(
            1
            for r in results
            if r.permission_leakage
        )

        latencies = [
            r.latency_ms
            for r in results
        ]

        latency_p95 = (
            EvaluationMetrics.latency_p95(
                latencies
            )
        )

        return EvaluationReport(
            retrieval_precision=round(
                retrieval_precision,
                3,
            ),
            citation_correctness=round(
                citation_correctness,
                3,
            ),
            answer_quality=round(
                answer_quality,
                3,
            ),
            permission_leakage_count=permission_leakage_count,
            latency_p95=round(
                latency_p95,
                2,
            ),
            total_questions=len(results),
            completed_at=datetime.now(),
            results_per_question=results,
        )
    


async def run_evaluation(
    *,
    sql_store: SQLStore,
    pipeline: RetrievalPipeline,
) -> EvaluationReport:
    """
    Public entry point for the evaluation framework.

    Used by the admin API and future background
    evaluation jobs.
    """

    runner = EvaluationRunner(
        sql_store=sql_store,
        pipeline=pipeline,
    )

    return await runner.run()