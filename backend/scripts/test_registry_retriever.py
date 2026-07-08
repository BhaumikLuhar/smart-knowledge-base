from core.retrieval.base_retriever import Retriever

from core.retrieval.registry import (
    register_retriever,
    inject_retriever,
    reset_retriever,
)


class NullRetriever(Retriever):

    def retrieve(
        self,
        query,
        user_context,
        top_k=None,
    ):
        return []


register_retriever(
    "null",
    NullRetriever,
)

inject_retriever("null")

print("✓ NullRetriever injected")

reset_retriever()

print("✓ Retriever registry restored")