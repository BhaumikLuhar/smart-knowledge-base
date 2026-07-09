import hashlib
import logging

from cachetools import TTLCache

from core.generation.schemas import ChatQueryResponse

logger = logging.getLogger(__name__)


class PipelineCache:
    """
    In-memory cache for complete chat responses.

    Cached value:
        ChatQueryResponse

    Cache isolation:
        user_id
        session_id
        normalized question

    This avoids rerunning the entire
    agent pipeline for repeated questions.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "PipelineCache":

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self):

        self.cache = TTLCache(
            maxsize=100,
            ttl=300,
        )

        self._hits = 0
        self._misses = 0
        self.user_index = {}

    @staticmethod
    def _normalize(question: str) -> str:

        return " ".join(
            question.strip().lower().split()
        )

    def _key(
        self,
        *,
        user_id: str,
        session_id: str,
        question: str,
    ) -> str:

        normalized = self._normalize(question)

        return hashlib.sha256(
            f"{user_id}:{session_id}:{normalized}".encode()
        ).hexdigest()

    def get(
        self,
        *,
        user_id: str,
        session_id: str,
        question: str,
    ) -> ChatQueryResponse | None:
        

        key = self._key(
            user_id=user_id,
            session_id=session_id,
            question=question,
        )

        response = self.cache.get(key)

        if response is None:
            self._misses += 1
            return None

        self._hits += 1

        logger.info(
            "Pipeline cache hit (hits=%s misses=%s)",
            self._hits,
            self._misses,
        )

        return response

    def set(
        self,
        *,
        user_id: str,
        session_id: str,
        question: str,
        response: ChatQueryResponse,
    ) -> None:
        

        key = self._key(
            user_id=user_id,
            session_id=session_id,
            question=question,
        )

        self.cache[key] = response

        self.user_index.setdefault(
            user_id,
            set(),
        ).add(key)

    def clear(self) -> None:

        self.cache.clear()

        logger.info("Pipeline cache cleared.")

    def clear_user(
        self,
        user_id: str,
    ) -> None:

        keys = self.user_index.pop(
            user_id,
            set(),
        )

        for key in keys:
            self.cache.pop(key, None)

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def size(self) -> int:
        return len(self.cache)