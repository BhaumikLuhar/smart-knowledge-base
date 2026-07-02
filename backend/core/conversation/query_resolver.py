import re

from core.generation.prompts import (
    QUERY_RESOLVER_SYSTEM_PROMPT_V1,QUERY_RESOLVER_SYSTEM_PROMPT_V2,
)
from core.generation.llm_provider import get_llm

MAX_ASSISTANT_CHARS = 250


class QueryResolver:
    """
    Resolves conversational follow-up questions into
    standalone retrieval queries.

    The resolver is intentionally conservative.

    It rewrites only when the current query clearly
    depends on previous conversation. Standalone
    questions are returned unchanged.
    """

    PRONOUN_PATTERN = re.compile(
        r"\b("
        r"it|its|this|that|these|those|"
        r"they|them|their|"
        r"he|him|his|"
        r"she|her|"
        r"such"
        r")\b",
        flags=re.IGNORECASE,
    )

    CONTINUATION_PATTERN = re.compile(
        r"^(?:"
        r"and\b|"
        r"also\b|"
        r"what about\b|"
        r"how about\b|"
        r"anything else\b|"
        r"what else\b|"
        r"tell me more\b|"
        r"more details\b|"
        r"continue\b|"
        r"go on\b"
        r")",
        flags=re.IGNORECASE,
    )

    SHORT_FOLLOW_UP_PATTERN = re.compile(
        r"^(?:"
        r"how many(?:\s+\w+){0,2}\??|"
        r"how long(?:\s+\w+){0,2}\??|"
        r"when\??|"
        r"where\??|"
        r"why\??|"
        r"who\??|"
        r"which one\??"
        r")$",
        flags=re.IGNORECASE,
    )

    ANSWER_PATTERN = re.compile(
        r"(according to|the policy|employees|states that|provides|receive|includes)",
        flags=re.IGNORECASE,
    )

    def _needs_resolution(
        self,
        query: str,
        history: list[dict],
    ) -> bool:
        """
        Determine whether the current query
        likely depends on previous conversation.
        """

        if not history:
            return False

        query = query.strip()

        if self.PRONOUN_PATTERN.search(query):
            return True

        if self.CONTINUATION_PATTERN.search(query):
            return True

        if self.SHORT_FOLLOW_UP_PATTERN.fullmatch(query):
            return True

        return False

    def _rewrite_with_llm(
        self,
        query: str,
        history: list[dict],
    ) -> str:
        """
        Rewrite the query into a standalone
        search query using conversation history.
        """

        conversation = []

        for message in history:

            role = message["role"].capitalize()

            content = message["content"].strip()

            if (
                message["role"] == "assistant"
                and len(content) > MAX_ASSISTANT_CHARS
            ):
                content = content[:MAX_ASSISTANT_CHARS] + "..."

            conversation.append(
                f"{role}: {content}"
            )

            conversation.append(
                f"{role}: {message['content']}"
            )

        messages = [
            {
                "role": "system",
                "content": QUERY_RESOLVER_SYSTEM_PROMPT_V2,
            },
            {
                "role": "user",
                "content": (
                    "Previous Conversation:\n\n"
                    + "\n".join(conversation)
                    + "\n\n"
                    "Latest User Question:\n"
                    + query
                ),
            },
        ]

        rewritten, _ = get_llm().generate(
            messages,
            temperature=0.0,
            max_tokens=128,
        )

        return rewritten.strip()

    def _is_valid_rewrite(
        self,
        original_query: str,
        rewritten_query: str,
    ) -> bool:
        """
        Validate the rewritten query before
        allowing it into the retrieval pipeline.
        """

        if not rewritten_query:
            return False

        if len(rewritten_query) > 200:
            return False

        if rewritten_query.endswith("."):
            return False

        if self.ANSWER_PATTERN.search(rewritten_query):
            return False

        if rewritten_query.lower() == original_query.lower():
            return False

        return True

    def resolve(
        self,
        query: str,
        history: list[dict],
    ) -> str:
        """
        Return a standalone query suitable
        for retrieval.
        """

        if not self._needs_resolution(
            query,
            history,
        ):
            return query

        try:

            rewritten = self._rewrite_with_llm(
                query,
                history,
            )

            if self._is_valid_rewrite(
                query,
                rewritten,
            ):
                return rewritten

        except Exception:
            #
            # Never block retrieval because
            # of query rewriting.
            #
            pass

        return query