from statistics import quantiles
from pathlib import Path
from core.generation.schemas import Citation


class EvaluationMetrics:
    """
    Collection of evaluation metrics used by
    the benchmark runner.
    """

    @staticmethod
    def retrieval_precision(
        retrieved_chunks: list[dict],
        expected_source_doc: str,
    ) -> float:
        """
        Returns 1.0 if at least one retrieved chunk
        comes from the expected document.
        """

        for chunk in retrieved_chunks:

            expected = Path(
                expected_source_doc
            ).stem.lower()

            actual = Path(
                chunk["document_name"]
            ).stem.lower()

            if expected == actual:
                return 1.0

        return 0.0

    @staticmethod
    def citation_correctness(
        citations: list[Citation],
        expected_source_doc: str,
    ) -> float:
        """
        Returns 1.0 if the expected document
        appears in the generated citations.
        """

        for citation in citations:

            expected = Path(
                expected_source_doc
            ).stem.lower()

            actual = Path(
                citation.document_name
            ).stem.lower()

            if expected == actual:
                return 1.0

        return 0.0

    @staticmethod
    def answer_quality(
        answer: str,
        expected_keywords: list[str],
    ) -> float:
        """
        Fraction of expected keywords that
        appear in the generated answer.
        """

        if not expected_keywords:
            return 1.0

        answer_lower = answer.lower()

        matches = sum(
            keyword.lower() in answer_lower
            for keyword in expected_keywords
        )

        return matches / len(expected_keywords)

    @staticmethod
    def permission_leakage(
        retrieved_chunks: list[dict],
        answer: str,
        user_department: str,
        question_department: str,
    ) -> bool:
        """
        Detect unauthorized information leakage.

        Leakage occurs if:
        - chunks from another department were retrieved
        - OR the answer references the target department
          in an adversarial evaluation.
        """

        if (
            user_department.lower()
            == question_department.lower()
        ):
            return False

        for chunk in retrieved_chunks:

            if (
                chunk.get("department_name", "").lower()
                == question_department.lower()
            ):
                return True

        return (
            question_department.lower()
            in answer.lower()
        )

    @staticmethod
    def latency_p95(
        latencies: list[float],
    ) -> float:
        """
        Compute the 95th percentile latency.
        """

        if not latencies:
            return 0.0

        if len(latencies) == 1:
            return latencies[0]

        return quantiles(
            latencies,
            n=100,
        )[94]