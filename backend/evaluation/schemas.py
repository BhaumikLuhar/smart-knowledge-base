from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EvaluationDatasetItem(BaseModel):

    question: str

    #
    # Department that OWNS the knowledge.
    #
    department_scope: str

    #
    # Department of the user executing
    # the benchmark.
    #
    evaluation_department: str

    expected_source_doc: str

    expected_keywords: list[str] = Field(
        default_factory=list
    )

    adversarial: bool = False


class EvaluationQuestionResult(BaseModel):
    """
    Result of executing one benchmark question.
    """

    question: str

    department_scope: str

    adversarial: bool

    answer: str

    expected_document: str

    retrieved_documents: list[str] = Field(
        default_factory=list
    )

    cited_documents: list[str] = Field(
        default_factory=list
    )

    retrieval_precision: float

    citation_correctness: float

    answer_quality: float

    permission_leakage: bool

    latency_ms: float

    confidence_score: float

    confidence_level: Literal[
        "low",
        "medium",
        "high",
    ]


class EvaluationReport(BaseModel):
    """
    Final report returned by the evaluation runner.
    """

    retrieval_precision: float

    citation_correctness: float

    answer_quality: float

    permission_leakage_count: int

    latency_p95: float

    total_questions: int

    completed_at: datetime

    results_per_question: list[
        EvaluationQuestionResult
    ] = Field(default_factory=list)