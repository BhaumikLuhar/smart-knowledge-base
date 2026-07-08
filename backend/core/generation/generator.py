from core.auth.user_context import UserContext
from core.generation.citation_builder import build_citations
from core.generation.llm_provider import get_llm
from core.generation.prompts import SYSTEM_PROMPT_V1
from core.generation.schemas import GeneratorResponse
from core.config import settings


class Generator:
    """
    Final RAG response generator.

    Converts retrieved chunks into a grounded,
    cited answer using the configured LLM.
    """

    FALLBACK_MESSAGE = (
        "I don't have authorized information to answer "
        "this question. Please contact your administrator "
        "if you believe you should have access."
    )

    def generate_response(
        self,
        query: str,
        chunks: list[dict],
        user_context: UserContext,
        history: list[dict] | None = None,
    ) -> GeneratorResponse:
        """
        Generate a grounded response.
        Parameters
        ----------
        query:
            User question.

        chunks:
            Authorized retrieved chunks.

        history:
            Previous conversation history
            formatted for the LLM.
        """

        #
        # Never call the LLM without context.
        #
        if not chunks:

            return GeneratorResponse(
                answer=self.FALLBACK_MESSAGE,
                citations=[],
                confidence_score=0.0,
                confidence_level="low",
                tokens_used=0,
                fallback=True,
                model_used=None,
            )
        
        history = history or []

        #
        # Build context
        #
        context = "\n\n".join(
            [
                (
                    f"[{i + 1}] "
                    f"Source: {chunk['document_name']}, "
                    f"Page "
                    f"{chunk['page_number'] if chunk['page_number'] >= 0 else 'Unknown'}\n"
                    f"{chunk['text']}"
                )
                for i, chunk in enumerate(chunks)
            ]
        )

        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT_V1,
        }

        user_message = {
            "role": "user",
            "content": (
                f"Context:\n"
                f"{context}\n\n"
                f"Question:\n"
                f"{query}"
            ),
        }

        messages = [
            system_message,
            *history,
            user_message,
        ]

        answer, tokens = get_llm().generate(
            messages
        )

        #
        # Confidence uses retrieval confidence rather
        # than reranker confidence.
        #
        top_score = chunks[0].get("hybrid_score", 0.0)

        chunk_count = len(chunks)

        if top_score > 0.75 and chunk_count >= 3:

            confidence_level = "high"

            confidence_score = max(
                80.0,
                min(round(top_score * 100, 1), 100.0),
            )

        elif top_score >= 0.5:

            confidence_level = "medium"

            confidence_score = max(
                50.0,
                min(round(top_score * 100, 1), 79.0),
            )

        else:

            confidence_level = "low"

            confidence_score = max(
                0.0,
                min(round(top_score * 100, 1), 49.0),
            )


        return GeneratorResponse(
            answer=answer,
            citations=build_citations(chunks),
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            tokens_used=tokens,
            fallback=False,
            model_used=settings.GROQ_MODEL,
        )