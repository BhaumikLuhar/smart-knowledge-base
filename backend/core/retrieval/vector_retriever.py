from core.auth.user_context import UserContext
from core.config import settings
from core.permissions.permission_service import PermissionService
from core.retrieval.base_retriever import Retriever
from core.retrieval.embedder import Embedder

from storage.sql.sql_store import SQLStore
from storage.vector.vector_store import VectorStore

# from core.profiling.profiler import profiler

class VectorRetriever(Retriever):
    """
    Semantic retrieval using Chroma.

    Retrieval flow:

    Query
      ->
    Embedder
      ->
    Chroma query
      ->
    Normalize results
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

        self.permission_service = PermissionService(
            sql_store
        )


    async def retrieve(self, query: str, user_context: UserContext, top_k: int | None=None)-> list[dict]:
        """
        Retrieve candidate chunks.

        Must respect user permissions.
        """

        top_k = top_k or settings.CANDIDATE_TOP_K
        # profiler.start("Query Embedding")
        query_embedding = Embedder.get_instance().embed_query(query)
        # profiler.stop("Query Embedding")

        # profiler.start("Permission Filter Build")
        chroma_filter = await self.permission_service.get_user_context_filters(user_context)
        # profiler.stop("Permission Filter Build")

        # profiler.start("Chroma Query")
        results = VectorStore.get_instance().query(
            query_embedding=query_embedding,
            top_k=top_k,
            where=chroma_filter
        )
        # profiler.stop("Chroma Query")

        # profiler.start("Vector Result Conversion")
        chunks=[]

        documents=results.get("documents",[[]])[0]

        metadatas=results.get("metadatas",[[]])[0]

        distcances=results.get("distances",[[]])[0]

        for text, metadata, distance in zip(documents, metadatas, distcances):

            similarity_score = max(0.0, 1 - float(distance))
            
            chunk={
                "chunk_id": metadata.get("chunk_id"),
                "document_id": metadata.get("document_id"),
                "document_name": metadata.get("document_name"),
                "text": text,
                "score": similarity_score,
                "department_id": metadata.get("department_id"),
                "visibility": metadata.get("visibility"),
                "page_number": metadata.get("page_number"),
                "chunk_index": metadata.get("chunk_index"),
            }

            chunks.append(chunk)

        chunks.sort(key=lambda x: x["score"], reverse=True)
        # profiler.stop("Vector Result Conversion")

        return chunks
