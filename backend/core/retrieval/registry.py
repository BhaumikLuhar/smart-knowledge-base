from typing import Type

from storage.sql.sql_store import SQLStore

from core.retrieval.base_retriever import Retriever
from core.retrieval.hybrid_retriever import HybridRetriever


RETRIEVER_REGISTRY: dict[str, Type[Retriever]] = {}

_ACTIVE_RETRIEVER = "default"

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
    name: str | None = None
) -> Retriever:
    """
    Create retriever instance.

    Default:
        HybridRetriever
    """

    selected = name or _ACTIVE_RETRIEVER

    retriever_class = RETRIEVER_REGISTRY.get(
        selected,
        HybridRetriever,
    )

    return retriever_class(sql_store)


def inject_retriever(name: str) -> None:
    """
    Switch the active retriever implementation.

    Intended for testing or controlled configuration.
    """

    if name not in RETRIEVER_REGISTRY:
        raise ValueError(
            f"Retriever '{name}' is not registered."
        )

    global _ACTIVE_RETRIEVER
    _ACTIVE_RETRIEVER = name


def reset_retriever() -> None:
    """
    Restore the default retriever.
    """

    global _ACTIVE_RETRIEVER
    _ACTIVE_RETRIEVER = "default"


register_retriever(
    "default",
    HybridRetriever
)

register_retriever(
    "hybrid",
    HybridRetriever
)