from datetime import datetime

import json

from storage.sql.sql_store import SQLStore

from core.admin.schemas import (
    AuditLogResponse,
    AuditLogEntry,
)


class AuditService:
    """
    Admin audit log service.
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    async def list_audit_logs(
            self,
            *,
            user_id: str | None = None,
            action: str | None = None,
            from_date: datetime | None = None,
            to_date: datetime | None = None,
            limit: int = 100,
            offset: int = 0,
    )-> AuditLogResponse:
        """
        List audit logs with optional filters.
        """

        conditions = []
        params = []

        if user_id:
            params.append(user_id)
            conditions.append(
                f"a.user_id = ${len(params)}"
            )

        if action:
            params.append(action)
            conditions.append(
                f"a.action = ${len(params)}"
            )

        if from_date:
            params.append(from_date)
            conditions.append(
                f"a.created_at >= ${len(params)}"
            )

        if to_date:
            params.append(to_date)
            conditions.append(
                f"a.created_at <= ${len(params)}"
            )

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        #
        # total count
        #
        count_sql = f"""
        SELECT COUNT(*)
        FROM audit_logs a
        {where_clause}
        """

        total = await self.sql_store.execute_raw(
            count_sql,
            tuple(params),
        )

        total_count = int(
            total[0]["count"]
        )

        #
        # paging
        #
        params.append(limit)
        params.append(offset)

        limit_index = len(params) - 1
        offset_index = len(params)

        sql = f"""
        SELECT

            a.*,

            u.email AS user_email

        FROM audit_logs a

        LEFT JOIN users u
            ON u.id = a.user_id

        {where_clause}

        ORDER BY a.created_at DESC

        LIMIT ${limit_index}
        OFFSET ${offset_index}
        """

        rows = await self.sql_store.execute_raw(
            sql,
            tuple(params),
        )

        items = []

        for row in rows:
            details = row["details"]

            if isinstance(details, str):
                details = json.loads(details)

            items.append(
                AuditLogEntry(
                    id=str(row["id"]),
                    user_id=(
                        str(row["user_id"])
                        if row["user_id"]
                        else None
                    ),
                    user_email=row["user_email"],
                    action=row["action"],
                    resource_type=row["resource_type"],
                    resource_id=row["resource_id"],
                    details=details,
                    ip_address=row["ip_address"],
                    created_at=row["created_at"],
                )
            )

        return AuditLogResponse(
            total=total_count,
            limit=limit,
            offset=offset,
            items=items,
        )