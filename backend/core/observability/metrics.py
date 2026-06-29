from storage.sql.sql_store import SQLStore


class MetricsRecorder:
    """
    Records endpoint execution metrics.

    Day 13:
        - success/failure
        - latency
        - token usage
        - retrieval count

    Future:
        - agent metrics
        - evaluation metrics
        - tracing
        - cost tracking
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    async def record(
        self,
        *,
        endpoint: str,
        user_id: str,
        latency: float,
        tokens: int,
        retrieval_count: int,
        status: str,
        error_message: str | None = None,
        agent_name: str | None = None,
    ) -> None:

        await self.sql_store.save(
            "metrics",
            {
                "endpoint": endpoint,
                "user_id": user_id,
                "latency": latency,
                "tokens": tokens,
                "status": status,
                "error_message": error_message,
                "agent_name": agent_name,
                "retrieval_count": retrieval_count,
            },
        )

    async def record_success(
        self,
        *,
        endpoint: str,
        user_id: str,
        latency: float,
        tokens: int,
        retrieval_count: int,
        agent_name: str | None = None,
    ) -> None:

        await self.record(
            endpoint=endpoint,
            user_id=user_id,
            latency=latency,
            tokens=tokens,
            retrieval_count=retrieval_count,
            status="success",
            agent_name=agent_name,
        )

    async def record_failure(
        self,
        *,
        endpoint: str,
        user_id: str,
        latency: float,
        retrieval_count: int = 0,
        error_message: str | None = None,
        agent_name: str | None = None,
    ) -> None:

        await self.record(
            endpoint=endpoint,
            user_id=user_id,
            latency=latency,
            tokens=0,
            retrieval_count=retrieval_count,
            status="failure",
            error_message=error_message,
            agent_name=agent_name,
        )