import time

from core.auth.user_context import UserContext
from core.chat.session_service import SessionService
from core.generation.generator import Generator
from core.generation.schemas import (
    ChatQueryResponse, GeneratorResponse
)

from core.observability.metrics import (
    MetricsRecorder,
)

from core.retrieval.retrieval_pipeline import (
    RetrievalPipeline,
)

from storage.sql.sql_store import SQLStore


class ChatService:
    """
    Handles the complete chat workflow.

    Responsibilities
    ----------------
    - Manage chat sessions
    - Persist chat messages
    - Execute retrieval
    - Generate grounded responses
    - Record metrics
    """

    def __init__(self, sql_store: SQLStore):

        self.sql_store = sql_store

        self.session_service = SessionService(
            sql_store
        )

        self.pipeline = RetrievalPipeline(
            sql_store
        )

        self.generator = Generator()

        self.metrics = MetricsRecorder(
            sql_store
        )

    async def _save_user_message(
        self,
        session_id: str,
        message: str,
    ) -> dict:
        """
        Persist a user message.
        """

        return await self.sql_store.save(
            "messages",
            {
                "session_id": session_id,
                "role": "user",
                "content": message,
            },
        )


    async def _save_assistant_message(
        self,
        session_id: str,
        response: GeneratorResponse,
        pipeline_result: dict,
    ) -> dict:
        """
        Persist assistant response.

        Rich metadata is stored for
        evaluation and analytics.
        """

        return await self.sql_store.save(
            "messages",
            {
                "session_id": session_id,
                "role": "assistant",
                "content": response.answer,
                "metadata": {
                    "citations": [
                        citation.model_dump()
                        for citation in response.citations
                    ],
                    "confidence": response.confidence,
                    "tokens_used": response.tokens_used,
                    "model_used": response.model_used,
                    "fallback": response.fallback,
                    "retrieved_chunks": pipeline_result["candidate_count"],
                    "authorized_chunks": pipeline_result["authorized_count"],
                    "returned_chunks": len(pipeline_result["chunks"]),
                },
            },
        )
    

    async def _execute_rag(
        self,
        message: str,
        current_user: UserContext,
    )-> tuple[dict, GeneratorResponse]:
        """
        Execute the complete retrieval and
        generation pipeline.
        """

        pipeline_result = await self.pipeline.retrieve_and_filter(
            query=message,
            user_context=current_user,
        )

        response = self.generator.generate_response(
            query=message,
            chunks=pipeline_result["chunks"],
            user_context=current_user,
        )

        return pipeline_result, response
    

    async def _record_success(
        self,
        *,
        user_id: str,
        latency: float,
        response: GeneratorResponse,
        retrieval_count: int,
    ) -> None:

        await self.metrics.record_success(
            endpoint="/api/v1/chat/query",
            user_id=user_id,
            latency=latency,
            tokens=response.tokens_used,
            retrieval_count=retrieval_count,
        )


    async def _record_failure(
        self,
        *,
        user_id: str,
        latency: float,
        error: Exception,
    ) -> None:

        await self.metrics.record_failure(
            endpoint="/api/v1/chat/query",
            user_id=user_id,
            latency=latency,
            retrieval_count=0,
            error_message=str(error),
        )


    async def query(
        self,
        *,
        message: str,
        session_id: str | None,
        current_user: UserContext,
    ) -> ChatQueryResponse:
        """
        Execute a complete RAG chat request.
        """

        start_time = time.perf_counter()

        session = await self.session_service.get_or_create_session(
            session_id=session_id,
            user_id=current_user.id,
        )

        pipeline_result = {
            "candidate_count": 0,
            "authorized_count": 0,
            "chunks": [],
        }

        try:

            #
            # Persist user message
            #
            await self._save_user_message(
                session_id=str(session["id"]),
                message=message,
            )

            #
            # Execute retrieval + generation
            #
            pipeline_result, response = await self._execute_rag(
                message=message,
                current_user=current_user,
            )

            #
            # Persist assistant response
            #
            await self._save_assistant_message(
                session_id=str(session["id"]),
                response=response,
                pipeline_result=pipeline_result,
            )

            latency = (
                time.perf_counter() - start_time
            ) * 1000

            #
            # Metrics
            #
            await self._record_success(
                user_id=current_user.id,
                latency=latency,
                response=response,
                retrieval_count=
                    pipeline_result["authorized_count"]
                ,
            )

            return ChatQueryResponse(
                session_id=str(session["id"]),
                answer=response.answer,
                citations=response.citations,
                confidence=response.confidence,
                tokens_used=response.tokens_used,
                fallback=response.fallback,
                model_used=response.model_used,
            )

        except Exception as exc:

            latency = (
                time.perf_counter() - start_time
            ) * 1000

            await self._record_failure(
                user_id=current_user.id,
                latency=latency,
                error=exc,
            )

            raise