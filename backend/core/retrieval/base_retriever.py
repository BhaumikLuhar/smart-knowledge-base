from abc import ABC, abstractmethod

from core.auth.user_context import UserContext


class Retriever(ABC):
    """
    Base retrieval contract.

    All retrieval strategies must return
    a normalized chunk format.

    Returned chunk structure:

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
    """

    @abstractmethod
    async def retrieve(self, query: str, user_context: UserContext, top_k: int | None=None) -> list[dict]:
        """
        Retrieve candidate chunks.

        Must respect user permissions.
        """
        pass