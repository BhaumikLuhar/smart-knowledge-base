from typing import Any
import json
import asyncpg
import uuid


class SQLStore:
    """
    Central PostgreSQL abstraction layer.

    All application services interact with the database
    through this class instead of writing raw SQL.
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, table: str, data: dict) -> dict:
        """
        INSERT row and return inserted record.
        """

        ALLOWED_TABLES = {
            "departments",
            "users",
            "documents",
            "document_versions",
            "chunks",
            "permissions",
            "sessions",
            "messages",
            "audit_logs",
            "metrics"
        }

        if table not in ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table: {table}"
            )

        columns = list(data.keys())
        values = []

        for value in data.values():
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            elif isinstance(value, uuid.UUID):
                values.append(str(value))
            else:
                values.append(value)

        placeholders = ", ".join(
            f"${i}"
            for i in range(1, len(columns)+1)
        )

        query = f"""
        INSERT INTO {table}
        ({', '.join(columns)})
        VALUES ({placeholders})
        RETURNING *;
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)

        return dict(row) if row else None

    async def bulk_insert_chunks(self, chunks: list[dict]) -> int:
        """
        Bulk insert chunk rows using a single
        INSERT statement.

        Returns:
            number of inserted rows
        """

        if not chunks:
            return 0

        values = []
        placeholders = []

        parameter_index = 1

        for chunk in chunks:
            placeholders.append(
                f"""
            (
                ${parameter_index},
                ${parameter_index + 1},
                ${parameter_index + 2},
                ${parameter_index + 3},
                ${parameter_index + 4},
                ${parameter_index + 5},
                ${parameter_index + 6}
            )
            """
            )

            values.extend(
                [
                    chunk["id"],
                    chunk["document_id"],
                    chunk["text"],
                    chunk["chunk_index"],
                    chunk["page_number"],
                    chunk["department_id"],
                    chunk["visibility"]
                ]
            )

            parameter_index += 7

        query = f"""
    INSERT INTO chunks (
        id,
        document_id,
        text,
        chunk_index,
        page_number,
        department_id,
        visibility
    )
    VALUES
    {",".join(placeholders)}
    """
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                *values
            )

        return len(chunks)

    async def query(self, table: str, filters: dict | None = None, order_by: str | None = None, limit: int | None = None) -> list[dict]:
        """
        SELECT rows with optional filters.
        """

        ALLOWED_TABLES = {
            "departments",
            "users",
            "documents",
            "document_versions",
            "chunks",
            "permissions",
            "sessions",
            "messages",
            "audit_logs",
            "metrics"
        }

        if table not in ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table: {table}"
            )

        filters = filters or {}

        sql = f"SELECT * FROM {table}"

        values = []

        if filters:
            clauses = []

            for index, (key, value) in enumerate(filters.items(), start=1):
                clauses.append(f"{key} = ${index}")
                values.append(value)

            sql += " WHERE " + " AND ".join(clauses)

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql += f" LIMIT {limit}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *values)

        return [dict(row) for row in rows]

    async def update(
        self,
        table: str,
        id: str,
        data: dict
    ) -> dict:
        """
        UPDATE row by ID and return updated record.
        """

        ALLOWED_TABLES = {
            "departments",
            "users",
            "documents",
            "document_versions",
            "chunks",
            "permissions",
            "sessions",
            "messages",
            "audit_logs",
            "metrics"
        }

        if table not in ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table: {table}"
            )

        columns = []
        values = []

        for key, value in data.items():

            if key == "updated_at" and value == "NOW()":
                columns.append(
                    f"{key} = NOW()"
                )
                continue

            columns.append(
                f"{key} = ${len(values)+1}"
            )

            if isinstance(
                value,
                (dict, list)
            ):
                values.append(
                    json.dumps(value)
                )
            else:
                values.append(value)

        set_clause = ", ".join(columns)

        query = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE id = ${len(values) + 1}
        RETURNING *;
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                *values,
                id
            )

        return dict(row) if row else {}

    async def delete(
        self,
        table: str,
        id: str
    ) -> bool:
        """
        Delete row by ID.
        """

        ALLOWED_TABLES = {
            "departments",
            "users",
            "documents",
            "document_versions",
            "chunks",
            "permissions",
            "sessions",
            "messages",
            "audit_logs",
            "metrics"
        }

        if table not in ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table: {table}"
            )

        query = f"""
        DELETE FROM {table}
        WHERE id = $1;
        """

        async with self.pool.acquire() as conn:
            result = await conn.execute(
                query,
                id
            )

        return result.startswith("DELETE")

    async def execute_raw(
        self,
        sql: str,
        params: tuple = ()
    ) -> list:
        """
        Escape hatch for complex joins,
        aggregations and reports.
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                sql,
                *params
            )

        return [dict(row) for row in rows]
