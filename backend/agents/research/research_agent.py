import time
import asyncio

from agents.base_agent import Agent
from agents.state import AgentState

from core.auth.user_context import UserContext
from core.config import settings
from core.retrieval.retrieval_pipeline import RetrievalPipeline

from core.observability.collector import (
    ObservabilityCollector,
)

from core.profiling.profiler import profiler


class ResearchAgent(Agent):
    """
    Executes permission-aware retrieval for the
    Planner's search queries.

    Responsibilities
    ----------------
    - Execute RetrievalPipeline for each search query.
    - Aggregate retrieved chunks.
    - Deduplicate overlapping results.
    - Keep the highest-ranked chunk.
    - Produce the final retrieval context for
      the Response Agent.

    SCOPE
    -----
    RAG-only retrieval.

    No internet access.
    No direct database access.
    No direct Chroma access.
    No LLM calls.

    All retrieval must go through RetrievalPipeline.
    """

    name = "research"

    def __init__(
        self,
        pipeline: RetrievalPipeline,
    ):
        self.pipeline = pipeline
        self.metrics = ObservabilityCollector(
            sql_store=pipeline.sql_store
        )

    async def execute(
        self,
        state: AgentState,
    ) -> AgentState:

        start = time.perf_counter()

        user_context = UserContext(**state["user_context"])

        queries = state["search_queries"]

        #
        # chunk_id -> best chunk
        #
        unique_chunks: dict[str, dict] = {}

        profiler.start(f"Research Retrieval [{", ".join(
            q[:30] for q in queries
        )}]")
        results = await asyncio.gather(
            *[
                self.pipeline.retrieve_and_filter(
                    query=query,
                    user_context=user_context,
                )
                for query in queries
            ]
        )
        profiler.stop(f"Research Retrieval [{", ".join(
            q[:30] for q in queries
        )}]")

        for result in results:
            for chunk in result["chunks"]:
                chunk_id = chunk["chunk_id"]

                existing = unique_chunks.get(chunk_id)

                if existing is None:
                    unique_chunks[chunk_id] = chunk
                    continue

                #
                # Keep the highest reranked chunk.
                #
                if (
                    chunk.get("rerank_score", float("-inf"))
                    >
                    existing.get(
                        "rerank_score",
                        float("-inf"),
                    )
                ):

                    unique_chunks[chunk_id] = chunk
        profiler.start("Research Deduplication + Sorting")
        final_chunks = sorted(
            unique_chunks.values(),
            key=lambda chunk: chunk.get(
                "rerank_score",
                float("-inf"),
            ),
            reverse=True,
        )[: settings.FINAL_TOP_K]

        state["retrieved_chunks"] = final_chunks
        profiler.stop("Research Deduplication + Sorting")

        state["no_results"] = len(final_chunks) == 0

        latency = (
            time.perf_counter() - start
        ) * 1000

        document_count = len(
            {
                chunk["document_id"]
                for chunk in final_chunks
            }
        )

        state["trace"].append(
            {
                "agent_name": self.name,
                "input_summary": (
                    f"{len(queries)} queries"
                ),
                "output_summary": (
                    f"{len(final_chunks)} unique chunks "
                    f"from {document_count} docs"
                ),
                "latency": round(
                    latency,
                    2,
                ),
            }
        )

        await self.metrics.record_agent_success(
            user_id=user_context.id,
            agent_name=self.name,
            latency=latency,
            tokens=0,
            retrieval_count=len(final_chunks),
        )

        # profiler.report()
        return state
