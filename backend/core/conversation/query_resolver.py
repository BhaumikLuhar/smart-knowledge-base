import json
import logging
import re

from core.generation.llm_provider import get_llm
from core.generation.prompts import QUERY_RESOLVER_SYSTEM_PROMPT_V3

from core.profiling.profiler import profiler


logger = logging.getLogger(__name__)

MAX_ASSISTANT_CHARS = 400
MAX_HISTORY_MESSAGES = 8
MAX_REWRITE_CHARS = 320

FOLLOW_UP_PREFIXES = (
    "and",
    "also",
    "same for",
    "same with",
    "same as",
    "same one",
    "what about",
    "how about",
    "what if",
    "continue",
    "tell me more",
    "more details",
    "explain more",
    "elaborate",
    "expand",
    "before",
    "after",
    "during",
)

SHORT_DEPENDENT_PREFIXES = (
    "how many",
    "how long",
    "how soon",
    "when",
    "where",
    "why",
    "who",
    "which",
    "what about",
    "how about",
    "what if",
)

REFUSAL_PATTERN = re.compile(
    r"^(?:"
    r"i'?m sorry|"
    r"i am sorry|"
    r"sorry|"
    r"as an ai|"
    r"i can'?t|"
    r"i cannot|"
    r"cannot help"
    r")",
    flags=re.IGNORECASE,
)

MULTILINE_OR_MARKUP_PATTERN = re.compile(
    r"\n|```|^\s*[-*•]\s+|^\s*#{1,6}\s+",
    flags=re.MULTILINE,
)


class QueryResolver:
    """
    Resolves conversational follow-up questions into standalone retrieval queries.

    The resolver rewrites only when the latest query clearly depends on prior
    conversation. Otherwise the original question is returned unchanged.
    """

    PRONOUN_PATTERN = re.compile(
        r"\b("
        r"it|its|this|that|these|those|"
        r"they|them|their|"
        r"he|him|his|"
        r"she|her|"
        r"such"
        r"here|there"
        r")\b",
        flags=re.IGNORECASE,
    )

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def _comparison_key(self, text: str) -> str:
        return re.sub(
            r"[.?!\s]+$",
            "",
            self._normalize_text(text),
        ).casefold()

    def _starts_with_phrase(
        self,
        text: str,
        phrase: str,
    ) -> bool:
        return re.match(
            rf"^{re.escape(phrase)}(?:\b|$)",
            text,
        ) is not None

    def _select_history(
        self,
        history: list[dict],
    ) -> list[dict]:
        selected = []

        for message in history:
            content = self._normalize_text(str(message.get("content", "")))

            if not content:
                continue

            role = str(message.get("role", "")).strip().lower()

            if role not in {"user", "assistant"}:
                continue

            selected.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        return selected[-MAX_HISTORY_MESSAGES:]

    def _resolution_decision(
        self,
        query: str,
        history: list[dict],
    ) -> tuple[bool, str]:
        """
        Decide whether the latest query depends on previous conversation.
        """

        if not history:
            return False, "no_history"

        normalized_query = self._normalize_text(query)

        if not normalized_query:
            return False, "empty_query"

        query_lower = normalized_query.casefold()

        if self.PRONOUN_PATTERN.search(query_lower):
            return True, "explicit_reference"

        for prefix in FOLLOW_UP_PREFIXES:
            if self._starts_with_phrase(query_lower, prefix):
                return True, f"continuation_phrase:{prefix}"

        if len(query_lower.split()) <= 6:
            for prefix in SHORT_DEPENDENT_PREFIXES:
                if self._starts_with_phrase(query_lower, prefix):
                    return True, f"short_dependent_question:{prefix}"

        return False, "standalone"

    def _build_messages(
        self,
        query: str,
        history: list[dict],
    ) -> list[dict]:
        selected_history = self._select_history(history)
        conversation = []

        for message in selected_history:
            role = message["role"].capitalize()
            content = message["content"]

            if role == "Assistant" and len(content) > MAX_ASSISTANT_CHARS:
                content = content[:MAX_ASSISTANT_CHARS].rstrip() + "..."

            conversation.append(f"{role}: {content}")

        history_block = "\n".join(conversation) if conversation else "(empty)"

        return [
            {
                "role": "system",
                "content": QUERY_RESOLVER_SYSTEM_PROMPT_V3,
            },
            {
                "role": "user",
                "content": (
                    "Previous Conversation:\n\n"
                    f"{history_block}\n\n"
                    "Latest User Question:\n"
                    f"{self._normalize_text(query)}"
                ),
            },
        ]

    def _rewrite_with_llm(
        self,
        query: str,
        history: list[dict],
    ) -> dict:
        """
        Rewrite the query into a standalone search query using conversation history.
        """

        messages = self._build_messages(
            query=query,
            history=history,
        )

        logger.debug(
            "QueryResolver prompt: %s",
            json.dumps(
                {"messages": messages},
                ensure_ascii=False,
                default=str,
            ),
        )

        provider = get_llm()

        finish_reason = None

        if hasattr(provider, "generate_with_metadata"):
            rewritten, tokens, metadata = provider.generate_with_metadata(
                messages,
                temperature=0.0,
                max_tokens=160,
            )

            if isinstance(metadata, dict):
                finish_reason = metadata.get("finish_reason")
        else:
            rewritten, tokens = provider.generate(
                messages,
                temperature=0.0,
                max_tokens=160,
            )

        rewritten_text = self._normalize_text(rewritten)

        logger.debug(
            "QueryResolver raw LLM output: %s",
            json.dumps(
                {
                    "raw_output": rewritten_text,
                    "finish_reason": finish_reason,
                    "tokens": tokens,
                },
                ensure_ascii=False,
                default=str,
            ),
        )

        return {
            "messages": messages,
            "raw_output": rewritten_text,
            "finish_reason": finish_reason,
            "tokens": tokens,
        }

    def _is_valid_rewrite(
        self,
        original_query: str,
        rewritten_query: str,
    ) -> tuple[bool, str]:
        """
        Validate the rewritten query before allowing it into the retrieval pipeline.
        """

        candidate = self._normalize_text(rewritten_query)

        if not candidate:
            return False, "empty_rewrite"

        if len(candidate) > MAX_REWRITE_CHARS:
            return False, "rewrite_too_long"

        if MULTILINE_OR_MARKUP_PATTERN.search(candidate):
            return False, "contains_multiline_or_markup"

        if candidate.startswith("{") or candidate.startswith("["):
            return False, "looks_like_json"

        if REFUSAL_PATTERN.match(candidate):
            return False, "model_refusal"

        if self._comparison_key(candidate) == self._comparison_key(original_query):
            return False, "same_as_original"

        return True, "accepted"

    def _finalize_rewrite(self, rewritten_query: str) -> str:
        candidate = self._normalize_text(rewritten_query)

        if not candidate:
            return candidate

        if candidate[-1] not in {"?", "!"}:
            candidate = candidate.rstrip(".") + "?"

        return candidate

    def resolve(
        self,
        query: str,
        history: list[dict],
    ) -> str:
        """
        Return a standalone query suitable for retrieval.
        """
        profiler.start("Query Resolver Decision")
        needs_resolution, decision_reason = self._resolution_decision(
            query,
            history,
        )
        profiler.stop("Query Resolver Decision")

        logger.debug(
            "QueryResolver decision: %s",
            json.dumps(
                {
                    "original_query": self._normalize_text(query),
                    "history_used": self._select_history(history),
                    "needs_resolution": needs_resolution,
                    "decision_reason": decision_reason,
                },
                ensure_ascii=False,
                default=str,
            ),
        )

        if not needs_resolution:
            final_query = self._normalize_text(query)

            logger.debug(
                "QueryResolver final output: %s",
                json.dumps(
                    {
                        "final_resolved_query": final_query,
                        "source": "original_query",
                    },
                    ensure_ascii=False,
                    default=str,
                ),
            )

            return query

        try:
            profiler.start("Query Resolver LLM")
            rewrite_attempt = self._rewrite_with_llm(
                query,
                history,
            )
            profiler.stop("Query Resolver LLM")

            profiler.start("Query Resolver Validation")
            is_valid, validation_reason = self._is_valid_rewrite(
                query,
                rewrite_attempt["raw_output"],
            )
            profiler.stop("Query Resolver Validation")

            if is_valid:
                final_query = self._finalize_rewrite(
                    rewrite_attempt["raw_output"],
                )

                logger.debug(
                    "QueryResolver validation: %s",
                    json.dumps(
                        {
                            "raw_llm_output": rewrite_attempt["raw_output"],
                            "finish_reason": rewrite_attempt["finish_reason"],
                            "validation_result": is_valid,
                            "validation_reason": validation_reason,
                            "final_resolved_query": final_query,
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                )

                logger.debug(
                    "QueryResolver final output: %s",
                    json.dumps(
                        {
                            "final_resolved_query": final_query,
                            "source": "rewritten_query",
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                )
                return final_query

            logger.debug(
                "QueryResolver validation: %s",
                json.dumps(
                    {
                        "raw_llm_output": rewrite_attempt["raw_output"],
                        "finish_reason": rewrite_attempt["finish_reason"],
                        "validation_result": is_valid,
                        "validation_reason": validation_reason,
                        "final_resolved_query": self._normalize_text(query),
                    },
                    ensure_ascii=False,
                    default=str,
                ),
            )

        except Exception as exc:
            logger.debug(
                "QueryResolver error: %s",
                json.dumps(
                    {
                        "error": str(exc),
                        "original_query": self._normalize_text(query),
                        "final_resolved_query": self._normalize_text(query),
                    },
                    ensure_ascii=False,
                    default=str,
                ),
                exc_info=True,
            )

        return query
