import hashlib
import json
import logging
import time

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Cache:
    """
    Cache BM25 indexes per permission scope.

    Each permission scope gets its own
    BM25 index.

    Cache expires after TTL or when
    marked dirty after ingestion.
    """

    _instance = None

    TTL_SECONDS = 300

    @classmethod
    def get_instance(cls):

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self):

        self._cache = {}
        self._dirty = False

    @staticmethod
    def build_scope_key(
        departments: list[str],
        visibilities: list[str],
    ) -> str:

        payload = {
            "departments": sorted(
                str(d) for d in departments
            ),
            "visibilities": sorted(visibilities),
        }

        return hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
            ).encode()
        ).hexdigest()

    def get(
        self,
        scope_key: str,
    ):
        

        if self._dirty:
            return None

        entry = self._cache.get(scope_key)

        if entry is None:
            return None

        age = time.time() - entry["timestamp"]

        if age > self.TTL_SECONDS:

            logger.info(
                "BM25 cache expired."
            )

            self._cache.pop(scope_key, None)

            return None

        logger.info(
            "BM25 cache hit."
        )

        return entry

    def set(
        self,
        scope_key: str,
        *,
        bm25: BM25Okapi,
        chunks: list,
    ):
        

        self._cache[scope_key] = {
            "bm25": bm25,
            "chunks": chunks,
            "timestamp": time.time(),
        }

        #
        # Corpus is now fresh.
        #
        self._dirty = False

    def mark_dirty(self):

        logger.info(
            "BM25 cache marked dirty."
        )

        self._dirty = True

    def clear(self):

        self._cache.clear()

        self._dirty = False