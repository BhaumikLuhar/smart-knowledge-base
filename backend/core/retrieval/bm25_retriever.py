import re

from rank_bm25 import BM25Okapi

from core.auth.user_context import UserContext
from core.config import settings
from core.permissions.permission_service import PermissionService
from core.retrieval.base_retriever import Retriever
from core.cache.bm25_cache import BM25Cache

from storage.sql.sql_store import SQLStore


class BM25Retriever(Retriever):
    """
    Keyword-based retrieval.

    Loads all accessible chunks for the user,
    builds a BM25 index in memory,
    ranks chunks by keyword relevance.
    """


    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store
        self.permission_service = PermissionService(sql_store)
        self.cache = BM25Cache.get_instance()


    async def _tokenize(self, text: str)-> list[dict]:
        """
        Basic tokenization.

        Lowercase and remove punctuation.
        """

        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)

        return text.split()
    

    async def retrieve(
        self,
        query: str,
        user_context: UserContext,
        top_k: int | None = None
    ) -> list[dict]:
        """
        Retrieve relevant chunks for a query.

        Uses BM25 ranking.
        """

        top_k = top_k or settings.CANDIDATE_TOP_K

        allowed_departments = await self.permission_service.get_allowed_departments(user_context)

        allowed_visibilities = await self.permission_service.get_allowed_visibilities(user_context)

        scope_key = self.cache.build_scope_key(
            allowed_departments,
            allowed_visibilities,
        )

        cached = self.cache.get(scope_key)

        if cached is not None:

            bm25 = cached["bm25"]
            chunks = cached["chunks"]

        else:

            sql = """
            SELECT
                c.id,
                c.chunk_index,
                c.text,
                c.document_id,
                c.department_id,
                c.page_number,
                c.visibility,
                d.name AS document_name
            FROM chunks c
            JOIN documents d
                ON d.id = c.document_id
            WHERE
                c.department_id = ANY($1::uuid[])
                AND c.visibility = ANY($2::text[])
                AND d.status != 'deleted'
            """

            chunks = await self.sql_store.execute_raw(
                sql,
                (allowed_departments, allowed_visibilities)
            )


            if not chunks:
                return []
            
            tokenized_corpus = [
                await self._tokenize(chunk["text"]) for chunk in chunks
            ]

            bm25 = BM25Okapi(tokenized_corpus)

            self.cache.set(
                scope_key,
                bm25=bm25,
                chunks=chunks,
            )

        tokenized_query = await self._tokenize(query)

        scores = bm25.get_scores(tokenized_query)

        max_score = max(scores) if len(scores) else 0

        results = []

        for chunk, score in zip(chunks, scores):
            normalized_score = float(score) / max_score if max_score > 0 else 0.0

            results.append(
                {
                    "chunk_id":
                        str(chunk["id"]),

                    "document_id":
                        str(
                            chunk["document_id"]
                        ),

                    "document_name":
                        chunk[
                            "document_name"
                        ],

                    "text":
                        chunk["text"],

                    "score":
                        normalized_score,

                    "department_id":
                        str(
                            chunk[
                                "department_id"
                            ]
                        ),

                    "visibility":
                        chunk[
                            "visibility"
                        ],

                    "page_number":
                        chunk[
                            "page_number"
                        ],
                    "chunk_index":
                        chunk[
                            "chunk_index"
                        ]
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]

            