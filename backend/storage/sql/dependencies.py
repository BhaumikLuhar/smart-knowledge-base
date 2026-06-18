from fastapi import Request

from storage.sql.sql_store import SQLStore


def get_sql_store(
    request: Request
) -> SQLStore:
    """
    FastAPI dependency.
    """

    return SQLStore(
        request.app.state.db_pool
    )