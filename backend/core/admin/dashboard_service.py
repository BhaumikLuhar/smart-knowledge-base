from storage.sql.sql_store import SQLStore

from core.admin.schemas import (
    RecentQuerySummary,
    DashboardSummaryResponse,
    HourlyQueryBucket,
    DepartmentQueryBreakdown,
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

        #
        # Query 1
        # Metrics aggregation
        #
        metrics = await self.sql_store.execute_raw(
            """
            SELECT

                COUNT(*) FILTER (
                    WHERE endpoint='/api/v1/chat/query'
                    AND status='success'
                    AND created_at::date=CURRENT_DATE
                ) AS today_queries,

                COUNT(*) FILTER (
                    WHERE status='error'
                    AND created_at::date=CURRENT_DATE
                ) AS today_errors,

                COALESCE(
                    ROUND(
                        AVG(latency)
                    ),
                    0
                ) AS avg_latency,

                COALESCE(
                    ROUND(
                        AVG(tokens)
                    ),
                    0
                ) AS avg_tokens,

                COUNT(
                    DISTINCT user_id
                ) FILTER (
                    WHERE endpoint='/api/v1/chat/query'
                    AND created_at::date=CURRENT_DATE
                ) AS active_users

            FROM metrics;
            """
        )

        metrics = metrics[0]

        #
        # Query 2
        # Documents
        #
        documents = await self.sql_store.execute_raw(
            """
            SELECT

                COUNT(*) AS total_documents,

                COUNT(*) FILTER (
                    WHERE status='ready'
                ) AS documents_ready

            FROM documents;
            """
        )

        documents = documents[0]

        #
        # Query 3
        # Permission denials
        #
        permission_rows = await self.sql_store.execute_raw(
            """
            SELECT COUNT(*) AS total
            FROM audit_logs
            WHERE
                action='permission_denied'
                AND created_at::date=CURRENT_DATE;
            """
        )

        permission_denials = int(
            permission_rows[0]["total"]
        )

        #
        # Query 4a
        # Department breakdown
        #
        department_rows = await self.sql_store.execute_raw(
            """
            SELECT

                d.display_name AS department,

                COUNT(*) AS query_count

            FROM audit_logs a

            JOIN users u
                ON u.id = a.user_id

            JOIN departments d
                ON d.id = u.department_id

            WHERE
                a.action='query'
                AND a.resource_type='chat'
                AND a.created_at::date=CURRENT_DATE

            GROUP BY
                d.display_name

            ORDER BY
                query_count DESC;
            """
        )

        total_queries = max(
            int(metrics["today_queries"]),
            1,
        )

        department_breakdown = []

        for row in department_rows:

            department_breakdown.append(

                DepartmentQueryBreakdown(

                    department=row["department"],

                    query_count=int(
                        row["query_count"]
                    ),

                    percentage=round(
                        (
                            int(row["query_count"])
                            / total_queries
                        )
                        * 100,
                        1,
                    ),
                )
            )

        #
        # Query 4b
        # Hourly volume
        #
        hourly_rows = await self.sql_store.execute_raw(
            """
            SELECT

                EXTRACT(
                    HOUR
                    FROM created_at
                )::INT AS hour,

                COUNT(*) AS query_count

            FROM audit_logs

            WHERE
                action='query'
                AND created_at::date=CURRENT_DATE

            GROUP BY hour

            ORDER BY hour;
            """
        )

        hourly_volume = []

        for row in hourly_rows:

            hourly_volume.append(

                HourlyQueryBucket(

                    hour=row["hour"],

                    query_count=int(
                        row["query_count"]
                    ),

                )

            )

        hour_counts = {
            int(row["hour"]): int(row["query_count"])
            for row in hourly_rows
        }

        hourly_volume = [
            HourlyQueryBucket(
                hour=hour,
                query_count=hour_counts.get(hour, 0),
            )
            for hour in range(24)
        ]

        #
        # Query 4c
        # Recent queries
        #
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
                ON u.id=a.user_id

            WHERE
                a.action='query'
                AND a.resource_type='chat'

            ORDER BY
                a.created_at DESC

            LIMIT 10;
            """
        )

        recent_queries = []

        for row in rows:

            recent_queries.append(

                RecentQuerySummary(

                    user=row["full_name"]
                    or "Unknown",

                    query=row["query"],

                    timestamp=row["created_at"],

                    confidence=row["confidence"],

                )

            )

        #
        # Day 23
        # Placeholder until evaluation framework
        #
        retrieval_precision = 0.0

        return DashboardSummaryResponse(

            total_queries_today=int(
                metrics["today_queries"]
            ),

            today_errors=int(
                metrics["today_errors"]
            ),

            average_latency_ms=int(
                metrics["avg_latency"]
            ),

            average_tokens=int(
                metrics["avg_tokens"]
            ),

            total_documents=int(
                documents["total_documents"]
            ),

            documents_ready=int(
                documents["documents_ready"]
            ),

            active_users=int(
                metrics["active_users"]
            ),

            permission_denials_today=permission_denials,

            retrieval_precision_avg=retrieval_precision,

            department_breakdown=department_breakdown,

            hourly_query_volume=hourly_volume,

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