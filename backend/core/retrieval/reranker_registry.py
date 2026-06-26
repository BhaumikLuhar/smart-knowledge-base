from typing import Type

from core.config import settings
from core.retrieval.base_reranker import Reranker
from core.retrieval.cross_encoder_reranker import (
    CrossEncoderReranker,
)
from core.retrieval.score_reranker import ScoreReranker


RERANKER_REGISTRY: dict[str, Type[Reranker]] = {}


def register_reranker(
    name: str,
    reranker_class: Type[Reranker]
) -> None:
    """
    Register a reranker implementation.
    """

    RERANKER_REGISTRY[name] = reranker_class


def get_reranker(name: str | None = None) -> Reranker:
    """
    Return the configured reranker.

    Falls back to the score reranker if the
    configured type is not registered.
    """

    reranker_class = RERANKER_REGISTRY.get(
        name or settings.RERANKER_TYPE,
        ScoreReranker
    )

    #
    # CrossEncoder uses a singleton.
    #
    if reranker_class is CrossEncoderReranker:
        return CrossEncoderReranker.get_instance()

    #
    # Lightweight rerankers can simply
    # be instantiated.
    #
    return reranker_class()


#
# Register built-in rerankers
#

register_reranker(
    "cross_encoder",
    CrossEncoderReranker
)

register_reranker(
    "score",
    ScoreReranker
)