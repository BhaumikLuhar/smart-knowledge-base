import logging

from storage.sql.sql_store import SQLStore

from core.observability.metrics import MetricsRecorder

logger = logging.getLogger(__name__)


class ObservabilityCollector:
    """
    Safe wrapper around MetricsRecorder.

    Responsibilities
    ----------------
    - Never allow observability failures
      to fail business requests.
    - Provide a single entry point for
      endpoint and agent metrics.
    """

    def __init__(self, sql_store: SQLStore):
        self.recorder = MetricsRecorder(sql_store)

    async def record_success(
        self,
        *,
        endpoint: str,
        user_id: str | None,
        latency: float,
        tokens: int = 0,
        retrieval_count: int = 0,
        agent_name: str | None = None,
    ) -> None:
        """
        Record successful execution.

        Metrics failures are intentionally
        ignored to avoid impacting user
        requests.
        """

        try:
            await self.recorder.record_success(
                endpoint=endpoint,
                user_id=user_id,
                latency=latency,
                tokens=tokens,
                retrieval_count=retrieval_count,
                agent_name=agent_name,
            )
        except Exception as e:
            logger.error(
                f"Failed to record success metrics: {e}"
            )

    async def record_failure(
        self,
        *,
        endpoint: str,
        user_id: str | None,
        latency: float,
        retrieval_count: int = 0,
        error_message: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        """
        Record failed execution.

        Never propagates observability
        exceptions.
        """

        try:
            await self.recorder.record_failure(
                endpoint=endpoint,
                user_id=user_id,
                latency=latency,
                retrieval_count=retrieval_count,
                error_message=error_message,
                agent_name=agent_name,
            )

        except Exception:
            logger.exception(
                "Failed to record failure metrics."
            )

    async def record_agent_success(
        self,
        *,
        user_id: str | None,
        agent_name: str,
        latency: float,
        tokens: int = 0,
        retrieval_count: int = 0,
    ) -> None:
        """
        Record successful execution of an agent.

        Uses the shared 'agent_pipeline'
        endpoint so dashboards can group
        all agent metrics together.
        """

        await self.record_success(
            endpoint="agent_pipeline",
            user_id=user_id,
            latency=latency,
            tokens=tokens,
            retrieval_count=retrieval_count,
            agent_name=agent_name,
        )


    async def record_agent_failure(
        self,
        *,
        user_id: str | None,
        agent_name: str,
        latency: float,
        error_message: str,
    ) -> None:
        """
        Record failed execution of an agent.
        """

        await self.record_failure(
            endpoint="agent_pipeline",
            user_id=user_id,
            latency=latency,
            retrieval_count=0,
            error_message=error_message,
            agent_name=agent_name,
        )