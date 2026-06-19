import asyncpg

from core.config import settings


async def create_db_pool():
    """
    Create PostgreSQL connection pool.
    Called once during FastAPI startup.
    """
    return await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        statement_cache_size=0,
        max_size=10,
        ssl="require"
    )


async def close_db_pool(pool):
    """
    Gracefully close PostgreSQL pool.
    Called during FastAPI shutdown.
    """
    if pool:
        await pool.close()