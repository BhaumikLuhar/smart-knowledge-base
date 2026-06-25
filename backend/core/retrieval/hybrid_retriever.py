from core.auth.user_context import UserContext
from core.config import settings
from core.retrieval.base_retriever import Retriever
from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.bm25_retriever import BM25Retriever

from storage.sql.sql_store import SQLStore


class HybridRetriever(Retriever):
    """
    Hybrid retrieval.

    Combines:
    - semantic search (vector)
    - keyword search (BM25)

    Final score:

    final =
        VECTOR_WEIGHT * vector_score
        +
        KEYWORD_WEIGHT * keyword_score
    """

    def __init__(
        self,
        sql_store: SQLStore
    ):
        self.sql_store = sql_store
        self.vector_retriever = VectorRetriever(sql_store)
        self.bm25_retriever = BM25Retriever(sql_store)
        

    async def retrieve(
            self,
            query: str,
            user_context: UserContext,
            top_k: int | None = None
    ) -> list[dict]:
        
        top_k = top_k or settings.CANDIDATE_TOP_K

        vector_results = await self.vector_retriever.retrieve(
            query,
            user_context,
            top_k=top_k
        )

        bm25_results = await self.bm25_retriever.retrieve(
            query,
            user_context,
            top_k=top_k
        )

        merged: dict[str, dict] = {}
        
        #
        # Add vector results
        #

        for chunk in vector_results:
            chunk_id= chunk["chunk_id"]

            merged[chunk_id] = {
                **chunk,
                "vector_score": chunk["score"],
                "bm25_score": 0.0
            }

        #
        # Add BM25 results
        #

        for chunk in bm25_results:

            chunk_id= chunk["chunk_id"]

            if chunk_id not in merged:
                merged[chunk_id] = {
                    **chunk,
                    "vector_score": 0.0,
                    "bm25_score": chunk["score"]
                }

            else:
                merged[chunk_id]["bm25_score"] = chunk["score"]

        #
        # Compute final score   
        #

        results = []

        for chunk in merged.values():
            final_score = (
                settings.VECTOR_WEIGHT * chunk["vector_score"]
                +
                settings.KEYWORD_WEIGHT * chunk["bm25_score"]
            )

            chunk["score"] = final_score
            chunk.pop("vector_score", None)
            chunk.pop("bm25_score", None)

            results.append(chunk)

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]