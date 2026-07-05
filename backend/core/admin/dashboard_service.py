from storage.sql.sql_store import SQLStore

from core.admin.schemas import (
    RecentQuerySummary,
    DashboardSummaryResponse,
)

from core.config import settings


class DashboardService:
    """
    Dashboard metrics for the admin UI.
    """

    def __init__(
        self,
        sql_store: SQLStore,
    ):
        self.sql_store = sql_store

    async def get_summary(
        self,
    ) -> DashboardSummaryResponse:

        total_queries = await self.sql_store.execute_raw(
            """
            SELECT COUNT(*) AS total
            FROM metrics
            WHERE
                endpoint = '/api/v1/chat/query'
                AND status = 'success'
                AND created_at::date = CURRENT_DATE;
            """
        )

        average_latency = await self.sql_store.execute_raw(
            """
            SELECT
                COALESCE(
                    ROUND(AVG(latency)),
                    0
                ) AS latency
            FROM metrics
            WHERE
                endpoint = '/api/v1/chat/query'
                AND status = 'success';
            """
        )

        active_users = await self.sql_store.execute_raw(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE is_active = TRUE;
            """
        )

        documents_ready = await self.sql_store.execute_raw(
            """
            SELECT COUNT(*) AS total
            FROM documents
            WHERE status = 'ready';
            """
        )

        rows = await self.sql_store.execute_raw(
            """
            SELECT

                u.full_name,

                COALESCE(
                    a.details->>'query',
                    '(not available)'
                ) AS query,

                a.created_at,

                COALESCE(
                    a.details->>'confidence_level',
                    'unknown'
                ) AS confidence

            FROM audit_logs a

            LEFT JOIN users u
                ON u.id = a.user_id

            WHERE a.action = 'query' AND a.resource_type = 'chat'

            ORDER BY a.created_at DESC

            LIMIT 10;
            """
        )

        recent_queries = []

        for row in rows:
            recent_queries.append(
                RecentQuerySummary(
                    user=row["full_name"] or "Unknown",
                    query=row["query"],
                    timestamp=row["created_at"],
                    confidence=row["confidence"],
                )
            )

        return DashboardSummaryResponse(
            total_queries_today=int(
                total_queries[0]["total"]
            ),
            average_latency_ms=int(
                average_latency[0]["latency"] or 0
            ),
            active_users=int(
                active_users[0]["total"]
            ),
            documents_ready=int(
                documents_ready[0]["total"]
            ),
            recent_queries=recent_queries,
        )
    


    async def get_system_config(
        self,
    ) -> dict:

        return {
            "chunk_size":
                settings.CHUNK_SIZE,

            "chunk_overlap":
                settings.CHUNK_OVERLAP,

            "candidate_top_k":
                settings.CANDIDATE_TOP_K,

            "final_top_k":
                settings.FINAL_TOP_K,

            "max_sessions":
                settings.MAX_SESSIONS,
        }