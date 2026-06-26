from storage.sql.sql_store import SQLStore

from core.auth.user_context import UserContext
from core.config import settings

from core.permissions.permission_service import PermissionService
from core.retrieval.registry import get_retriever
from core.retrieval.reranker_registry import get_reranker


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
                final=[]
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
                final=[]
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
        print("\n--- BEFORE RERANK ---")
        for chunk in authorized[:5]:
            print(
                round(chunk["score"], 4),
                chunk["document_name"]
            )

        reranked = self.reranker.rerank(
            query=query,
            candidates=authorized
        )

        print("\n--- AFTER RERANK ---")
        for chunk in reranked[:5]:
            print(
                round(chunk["score"], 4),
                chunk["document_name"]
            )
        #
        # Stage 4
        # Final Top-K
        #
        final = reranked[:settings.FINAL_TOP_K]

        #
        # Stage 5
        # Audit log
        #

        await self._log_query(
            query=query,
            user_context=user_context,
            candidates=candidates,
            authorized=authorized,
            final=final
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
        final: list[dict]
    ) -> None:
        """
        Store retrieval audit trail.

        Every retrieval pipeline execution
        is recorded for compliance.
        """

        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": user_context.id,
                "action": "query",
                "details": {
                    "query_text": query,
                    "candidate_count": len(candidates),
                    "authorized_count": len(authorized),
                    "final_count": len(final),
                    "doc_ids_returned": list({
                        chunk["document_id"]
                        for chunk in final
                    }),
                    "chunk_ids_returned": [
                        chunk["chunk_id"]
                        for chunk in final
                    ],
                    "candidate_chunk_ids": [
                        chunk["chunk_id"]
                        for chunk in candidates
                    ],
                    "authorized_doc_ids": list({
                        chunk["document_id"]
                        for chunk in authorized
                    }),
                }
            }
        )