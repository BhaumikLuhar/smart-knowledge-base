import asyncio

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore
from core.knowledge.ingestion_service import ingest_document


async def main():

    pool = await create_db_pool()

    store = SQLStore(pool)

    document_id = input(
        "Document UUID: "
    )

    await ingest_document(
        document_id,
        store
    )

    await pool.close()


asyncio.run(main())