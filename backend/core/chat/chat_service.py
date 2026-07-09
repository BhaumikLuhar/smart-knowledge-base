import asyncio
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

from core.cache.pipeline_cache import PipelineCache

# from core.profiling.profiler import profiler


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

        self.pipeline_cache = PipelineCache.get_instance()

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

    async def _record_query_audit(
        self,
        *,
        user_id: str,
        session_id: str,
        query: str,
        state: dict,
    ) -> None:

        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": user_id,
                "action": "query",
                "resource_type": "chat",
                "resource_id": session_id,
                "details": {
                    "query": query,
                    "confidence_level":
                        state["confidence_level"],
                    "confidence_score":
                        state["confidence_score"],
                },
            },
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
        # profiler.reset()

        # profiler.start("Session Lookup")
        session = await self.session_service.get_or_create_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        # profiler.stop("Session Lookup")

        cached = self.pipeline_cache.get(
            user_id=current_user.id,
            session_id=str(session["id"]),
            question=message,
        )

        if cached is not None:

            await asyncio.gather(
                self._save_user_message(
                    session_id=str(session["id"]),
                    message=message,
                ),

                self._save_assistant_message(
                    session_id=str(session["id"]),
                    state={
                        "answer": cached.answer,
                        "citations": cached.citations,
                        "confidence_score": cached.confidence_score,
                        "confidence_level": cached.confidence_level,
                        "tokens_used": cached.tokens_used,
                        "planner_tokens_used": 0,
                        "resolved_query": "",
                        "trace": cached.trace,
                    },
                ),

                self._record_success(
                    user_id=current_user.id,
                    latency=1,
                    tokens_used=0,
                    retrieval_count=0,
                ),
            )

            return cached

        try:
            #
            # Execute retrieval + generation
            #
            # profiler.start("Complete Agent Workflow")
            state = await run_agent_pipeline(
                query=message,
                user_context=current_user,
                session_id=str(session["id"]),
                pipeline=self.pipeline,
            )
            # profiler.stop("Complete Agent Workflow")

            latency = (
                time.perf_counter() - start_time
            ) * 1000

            #
            # Persist everything in parallel.
            #
            # profiler.start("Parallel Persistence")

            results = await asyncio.gather(

                #
                # Persist user message
                #
                self._save_user_message(
                    session_id=str(session["id"]),
                    message=message,
                ),

                #
                # Persist assistant response
                #
                self._save_assistant_message(
                    session_id=str(session["id"]),
                    state=state,
                ),

                #
                # Metrics
                #
                self._record_success(
                    user_id=current_user.id,
                    latency=latency,
                    tokens_used=(
                        state["tokens_used"]
                        + state["planner_tokens_used"]
                    ),
                    retrieval_count=len(
                        state["retrieved_chunks"]
                    ),
                ),

                #
                # Audit log
                #
                self._record_query_audit(
                    user_id=current_user.id,
                    session_id=str(session["id"]),
                    query=message,
                    state=state,
                ),

                return_exceptions=True,
            )

            # profiler.stop("Parallel Persistence")

            #
            # Preserve existing failure behaviour.
            #
            for result in results:
                if isinstance(result, Exception):
                    raise result

            response = ChatQueryResponse(
                session_id=str(session["id"]),
                answer=state["answer"],
                citations=state["citations"],
                confidence_score=state["confidence_score"],
                confidence_level=state["confidence_level"],
                tokens_used=(
                    state["tokens_used"]
                    + state["planner_tokens_used"]
                ),
                fallback=state["no_results"],
                model_used=settings.GROQ_MODEL,
                trace=state["trace"],
            )

            self.pipeline_cache.set(
                user_id=current_user.id,
                session_id=str(session["id"]),
                question=message,
                response=response,
            )

            # profiler.report()
            return response

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
