import asyncio
from pathlib import Path
import sys

import asyncpg
sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.config import settings


MIGRATIONS_DIR = (
    Path(__file__)
    .parent.parent
    / "storage"
    / "sql"
    / "migrations"
)


CREATE_MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    executed_at TIMESTAMP DEFAULT now()
);
"""


async def ensure_migration_table(conn):
    await conn.execute(CREATE_MIGRATION_TABLE)


async def migration_already_applied(
    conn,
    filename: str
) -> bool:
    row = await conn.fetchrow(
        """
        SELECT filename
        FROM schema_migrations
        WHERE filename = $1
        """,
        filename,
    )

    return row is not None


async def mark_migration_applied(
    conn,
    filename: str
):
    await conn.execute(
        """
        INSERT INTO schema_migrations (filename)
        VALUES ($1)
        """,
        filename,
    )


async def run_migrations():
    conn = await asyncpg.connect(
        settings.DATABASE_URL,
        statement_cache_size=0,
        ssl="require"
    )

    try:
        await ensure_migration_table(conn)

        migration_files = sorted(
            MIGRATIONS_DIR.glob("*.sql")
        )

        for migration_file in migration_files:

            filename = migration_file.name

            already_applied = (
                await migration_already_applied(
                    conn,
                    filename
                )
            )

            if already_applied:
                print(
                    f"⏭ Skipping {filename}"
                )
                continue

            print(
                f"▶ Running {filename}"
            )

            sql = migration_file.read_text(
                encoding="utf-8"
            )

            async with conn.transaction():
                await conn.execute(sql)

                await mark_migration_applied(
                    conn,
                    filename
                )

            print(
                f"✅ Completed {filename}"
            )

        print(
            "\n🎉 All migrations complete"
        )

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())