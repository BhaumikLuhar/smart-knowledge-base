from storage.sql.sql_store import SQLStore

from core.auth.user_context import UserContext
from core.config import settings

from core.permissions.permission_service import PermissionService
from core.retrieval.registry import get_retriever
from core.retrieval.reranker_registry import get_reranker

import logging

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """
    End-to-end retrieval pipeline.

    Flow

        Query
          │
          ▼
    Hybrid Retriever
          │
          ▼
    Candidate Chunks
          │
          ▼
    Permission Filter
          │
          ▼
    Reranker (Day 12)
          │
          ▼
    Final Top-K
          │
          ▼
    Audit Log
    """


    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store
        self.permission_service = PermissionService(sql_store)
        self.retriever = get_retriever(sql_store)
        self.reranker = get_reranker()


    async def retrieve_and_filter(
        self,
        query: str,
        user_context: UserContext,
    ) -> dict:
        """
        Retrieve candidate chunks and apply
        permission filtering.

        Returns
        -------
        {
            "chunks": [],
            "candidate_count": int,
            "authorized_count": int,
            "query": str
        }
        """
        quality_gate=None

        #
        # Stage 1
        # Candidate Retrieval
        # 
        candidates = await self.retriever.retrieve(
            query=query,
            user_context=user_context,
            top_k=settings.CANDIDATE_TOP_K
        )

        #
        # Nothing indexed
        #
        if not candidates:
            await self._log_query(
                query=query,
                user_context=user_context,
                candidates=[],
                authorized=[],
                final=[],
                quality_gate=quality_gate,
            )
            
            return {
                "chunks": [],
                "candidate_count": 0,
                "authorized_count": 0,
                "query": query,
                "message": (
                    "No documents have been indexed yet. "
                    "Please contact your administrator."
                )
            }
        
        #
        # Stage 2
        # Secondary permission check
        #
        authorized = await self.permission_service.filter_chunks(
            user_context,
            candidates
        )

        #
        # No authorized documents
        #
        if not authorized:
            await self._log_query(
                query=query,
                user_context=user_context,
                candidates=candidates,
                authorized=[],
                final=[],
                quality_gate=quality_gate,
            )

            return {
                "chunks": [],
                "candidate_count": len(candidates),
                "authorized_count": 0,
                "query": query,
                "message": (
                    "No authorized documents found "
                    "for this query."
                )
            }
        
        #
        # Stage 3
        # Rerank authorized chunks
        #
        reranked = self.reranker.rerank(
            query=query,
            candidates=authorized
        )

        #
        # Stage 4
        # Final Top-K
        #
        final = reranked[:settings.FINAL_TOP_K]

        #
        # Stage 4a
        # Relevance quality gate
        #
        if (
            final
            and final[0].get("rerank_score", float("-inf"))
            < settings.MIN_RERANK_SCORE
        ):

            logger.info(
                "Relevance gate triggered. "
                "Top rerank score %.3f below threshold %.3f.",
                final[0]["rerank_score"],
                settings.MIN_RERANK_SCORE,
            )

            quality_gate = {
                "triggered": True,
                "type": "rerank",
                "score": final[0]["rerank_score"],
                "threshold": settings.MIN_RERANK_SCORE,
            }
            final = []

        #
        # Stage 4b
        # Retrieval quality gate
        #
        elif (
            final
            and final[0].get("hybrid_score", 0.0)
            < settings.MIN_RETRIEVAL_SCORE
        ):

            logger.info(
                "Retrieval quality gate triggered. "
                "Top hybrid score %.3f below threshold %.3f.",
                final[0]["hybrid_score"],
                settings.MIN_RETRIEVAL_SCORE,
            )

            quality_gate = {
                "triggered": True,
                "type": "hybrid",
                "score": final[0]["hybrid_score"],
                "threshold": settings.MIN_RETRIEVAL_SCORE,
            }
            final = []

        #
        # Stage 5
        # Audit log
        #

        await self._log_query(
            query=query,
            user_context=user_context,
            candidates=candidates,
            authorized=authorized,
            final=final,
            quality_gate=quality_gate,
        )

        return {
            "chunks": final,
            "candidate_count": len(candidates),
            "authorized_count": len(authorized),
            "query": query
        }
    

    async def _log_query(
        self,
        query: str,
        user_context: UserContext,
        candidates: list[dict],
        authorized: list[dict],
        final: list[dict],
        quality_gate: dict | None = None,
    ) -> None:
        """
        Store retrieval audit trail.

        Every retrieval pipeline execution
        is recorded for compliance and
        security verification.
        """

        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": user_context.id,
                "action": "query",
                "details": {
                    "query_text": query,

                    #
                    # Retrieval statistics
                    #
                    "candidate_count": len(candidates),
                    "authorized_count": len(authorized),
                    "final_count": len(final),

                    #
                    # Quality gate (if triggered)
                    #
                    "quality_gate": quality_gate,

                    #
                    # Returned documents
                    #
                    "doc_ids_returned": list({
                        chunk["document_id"]
                        for chunk in final
                    }),

                    "authorized_doc_ids": list({
                        chunk["document_id"]
                        for chunk in authorized
                    }),

                    #
                    # Final chunks returned to the LLM
                    #
                    "returned_chunks": [
                        {
                            "chunk_id": chunk["chunk_id"],
                            "document_id": chunk["document_id"],
                            "document_name": chunk["document_name"],
                            "department_id": chunk["department_id"],
                            "visibility": chunk["visibility"],
                            "hybrid_score": round(
                                chunk.get("hybrid_score", 0.0), 3
                            ),
                            "rerank_score": round(
                                chunk.get("rerank_score", 0.0), 3
                            ),
                        }
                        for chunk in final
                    ],

                    #
                    # Candidate chunk ids
                    #
                    "candidate_chunk_ids": [
                        chunk["chunk_id"]
                        for chunk in candidates
                    ],
                },
            },
        )