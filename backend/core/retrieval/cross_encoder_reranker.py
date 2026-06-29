import logging

from sentence_transformers import CrossEncoder

from core.config import settings
from core.retrieval.base_reranker import Reranker


logger = logging.getLogger(__name__)


class CrossEncoderReranker(Reranker):
    """
    Cross-encoder based reranker.

    Uses a sentence-transformers CrossEncoder to
    rescore retrieved candidate chunks.

    Unlike embedding similarity, a cross encoder
    jointly encodes the query and document, producing
    a more accurate relevance score.

    Singleton pattern is used to avoid repeatedly
    loading the model (~80MB).
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CrossEncoderReranker()
        return cls._instance
    

    def __init__(self):
        #
        # Prevent reloading
        #
        if hasattr(self, "model"):
            return
        
        logger.info(
            "Loading CrossEncoder model: %s",
            settings.CROSS_ENCODER_MODEL
        )

        self.model = CrossEncoder(
            settings.CROSS_ENCODER_MODEL
        )

        logger.info(
            "CrossEncoder model loaded successfully."
        )


    def rerank(
            self,
            query: str,
            candidates: list[dict]
    )-> list[dict]:
        """
        Rerank candidate chunks using the
        cross-encoder relevance model.
        """

        if not candidates:
            return []

        #
        # Build (query, passage) pairs
        #
        pairs = [
            (
                query,
                chunk["text"]
            )
            for chunk in candidates
        ]

        #
        # Batch inference
        #
        scores = self.model.predict(
            pairs,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        reranked = []

        for chunk, score in zip(candidates, scores):

            #
            # Preserve structure
            #
            updated_chunk = chunk.copy()

            updated_chunk["hybrid_score"] = updated_chunk["score"]

            updated_chunk["rerank_score"] = float(score)

            updated_chunk["score"] = float(score)

            reranked.append(updated_chunk)

        
        reranked.sort(
            key=lambda chunk: chunk.get("score", 0.0),
            reverse=True
        )

        logger.debug(
            "CrossEncoder reranked %d candidates.",
            len(reranked)
        )

        return reranked
