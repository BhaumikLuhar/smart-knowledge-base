import time

from core.auth.user_context import UserContext
from core.chat.session_service import SessionService
from agents.workflow import run_agent_pipeline

from core.generation.schemas import (
    ChatQueryResponse,
)

from core.observability.collector import (
    ObservabilityCollector,
)

from core.retrieval.retrieval_pipeline import (
    RetrievalPipeline,
)

from storage.sql.sql_store import SQLStore

from core.config import settings


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

        self.metrics = ObservabilityCollector(
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
        state: dict,
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
                "content": state.get("answer"),
                "metadata": {
                    "citations": [
                        citation.model_dump()
                        for citation in state["citations"]
                    ],
                    "resolved_query": state["resolved_query"],
                    "confidence_score": state["confidence_score"],
                    "confidence_level": state["confidence_level"],
                    "tokens_used": state["tokens_used"]+state["planner_tokens_used"],
                    "trace": state["trace"],
                },
            },
        )

    

    async def _record_success(
        self,
        *,
        user_id: str,
        latency: float,
        tokens_used: int,
        retrieval_count: int,
    ) -> None:

        await self.metrics.record_success(
            endpoint="/api/v1/chat/query",
            user_id=user_id,
            latency=latency,
            tokens=tokens_used,
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
            # Execute retrieval + generation
            #
            state = await run_agent_pipeline(
                query=message,
                user_context=current_user,
                session_id=str(session["id"]),
                pipeline=self.pipeline,
            )

            #
            # Persist user message
            #
            await self._save_user_message(
                session_id=str(session["id"]),
                message=message,
            )

            #
            # Persist assistant response
            #
            await self._save_assistant_message(
                session_id=str(session["id"]),
                state=state,
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
                tokens_used=state["tokens_used"] + state["planner_tokens_used"],
                retrieval_count=len(
                    state["retrieved_chunks"]
                ),
            )

            return ChatQueryResponse(
                session_id=str(session["id"]),
                answer=state["answer"],
                citations=state["citations"],
                confidence_score=state["confidence_score"],
                confidence_level=state["confidence_level"],
                tokens_used=state["tokens_used"] + state["planner_tokens_used"],
                fallback=state["no_results"],
                model_used=settings.GROQ_MODEL,
                trace=state["trace"],
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