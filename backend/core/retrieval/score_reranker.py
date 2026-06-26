import logging 

from core.retrieval.base_reranker import Reranker


logger = logging.getLogger(__name__)


class ScoreReranker(Reranker):
    """
    Score-based reranker.

    This reranker performs no additional inference.

    It simply sorts candidate chunks using the
    existing hybrid retrieval score.

    Used as:

    - fallback when CrossEncoder is unavailable
    - lightweight deployment option
    - benchmarking baseline
    """

    def rerank(
            self,
            query: str,
            candidates: list[dict]
    )-> list[dict]:
        """
        Sort candidates using the existing score.
        """

        if not candidates:
            return []

        reranked = sorted(
            candidates,
            key=lambda chunk: chunk.get("score", 0.0),
            reverse=True
        )

        logger.debug(
            "ScoreReranker reranked %d candidates.",
            len(reranked)
        )

        return reranked