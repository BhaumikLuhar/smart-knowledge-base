from typing import Any
import json
import asyncpg

class SQLStore:
    """
    Central PostgreSQL abstraction layer.

    All application services interact with the database
    through this class instead of writing raw SQL.
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, table: str, data: dict)->dict:
        """
        INSERT row and return inserted record.
        """

        columns=list(data.keys())
        values = []

        for value in data.values():
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            else:
                values.append(value)

        placeholders= ", ".join(
            f"${i}"
            for i in range(1,len(columns)+1)
        )

        query = f"""
        INSERT INTO {table}
        ({', '.join(columns)})
        VALUES ({placeholders})
        RETURNING *;
        """

        async with self.pool.acquire() as conn:
            row= await conn.fetchrow(query, *values)

        return dict(row) if row else None
    

    async def query(self, table: str, filters: dict | None=None, order_by: str | None=None, limit: int | None=None)->list[dict]:
        """
        SELECT rows with optional filters.
        """

        filters=filters or {}

        sql=f"SELECT * FROM {table}"

        values=[]

        if filters:
            clauses=[]

            for index, (key,value) in enumerate(filters.items(), start=1):
                clauses.append(f"{key} = ${index}")
                values.append(value)

            sql+= " WHERE " + " AND ".join(clauses)
        
        if order_by:
            sql+= f" ORDER BY {order_by}"

        if limit:
            sql+= f" LIMIT {limit}"

        async with self.pool.acquire() as conn:
            rows= await conn.fetch(sql, *values)

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

        columns = list(data.keys())
        values = list(data.values())

        set_clause = ", ".join(
            f"{column} = ${i}"
            for i, column in enumerate(columns, start=1)
        )

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
