import math

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
    ) -> GeneratorResponse:
        """
        Generate a grounded response.
        """

        #
        # Never call the LLM without context.
        #
        if not chunks:

            return GeneratorResponse(
                answer=self.FALLBACK_MESSAGE,
                citations=[],
                confidence=0,
                tokens_used=0,
                fallback=True,
                model_used=None,
            )

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

        answer, tokens = get_llm().generate(
            [
                system_message,
                user_message,
            ]
        )

        hybrid_scores = [
            chunk.get("hybrid_score", 0.0)
            for chunk in chunks[:3]
        ]

        average_similarity = (
            sum(hybrid_scores)
            / len(hybrid_scores)
        )

        
        confidence = max(
            0.0,
            min(
                round(average_similarity * 100, 1),
                100.0,
            ),
        )

        print("\n--- CONFIDENCE ---")

        for chunk in chunks:
            print(
                "Retrieval:",
                round(chunk["hybrid_score"], 3),
                "Rerank:",
                round(chunk["rerank_score"], 3),
            )

        print("Confidence:", confidence)

        return GeneratorResponse(
            answer=answer,
            citations=build_citations(chunks),
            confidence=confidence,
            tokens_used=tokens,
            fallback=False,
            model_used=settings.GROQ_MODEL,
        )