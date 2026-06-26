from abc import ABC, abstractmethod


class Reranker(ABC):
    """
    Base reranker contract.

    A reranker receives candidate chunks that have
    already passed retrieval and permission filtering,
    then returns the same chunks ordered by relevance.

    Input chunk format:

    {
        "chunk_id": str,
        "document_id": str,
        "document_name": str,
        "text": str,
        "score": float,
        "department_id": str,
        "visibility": str,
        "page_number": int
    }

    Notes
    -----
    - Do NOT modify the chunk structure.
    - Updating the "score" field is allowed.
    - Return the same chunks sorted best-first.
    """

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[dict]
    ) -> list[dict]:
        """
        Rerank candidate chunks.

        Parameters
        ----------
        query:
            Original user query.

        candidates:
            Candidate chunks produced by the
            retrieval pipeline.

        Returns
        -------
        list[dict]

            Same chunk objects sorted by
            descending relevance.
        """
        raise NotImplementedError