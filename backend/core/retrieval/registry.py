from typing import Type

from storage.sql.sql_store import SQLStore

from core.retrieval.base_retriever import Retriever
from core.retrieval.hybrid_retriever import HybridRetriever


RETRIEVER_REGISTRY: dict[str, Type[Retriever]] = {}


def register_retriever(
    name: str,
    retriever_class: Type[Retriever]
) -> None:
    """
    Register a retriever implementation.
    """

    RETRIEVER_REGISTRY[name] = retriever_class


def get_retriever(
    sql_store: SQLStore,
    name: str = "default"
) -> Retriever:
    """
    Create retriever instance.

    Default:
        HybridRetriever
    """

    retriever_class = (
        RETRIEVER_REGISTRY.get(
            name,
            HybridRetriever
        )
    )

    return retriever_class(sql_store)


register_retriever(
    "default",
    HybridRetriever
)

register_retriever(
    "hybrid",
    HybridRetriever
)