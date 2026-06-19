import asyncio
import asyncpg

from core.config import settings


async def test_connection():
    conn = await asyncpg.connect(settings.DATABASE_URL,ssl="require",statement_cache_size=0,ssl="require")

    try:
        version = await conn.fetchval(
            "SELECT version();"
        )

        print("\nSUCCESS")
        print(version)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_connection())