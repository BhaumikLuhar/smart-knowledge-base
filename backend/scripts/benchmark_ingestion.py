import asyncio
import time

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore
from core.knowledge.ingestion_service import (
    ingest_document
)


async def benchmark(
    document_ids: list[str]
):

    pool = await create_db_pool()

    store = SQLStore(pool)

    start = time.perf_counter()

    for document_id in document_ids:

        try:
            await ingest_document(
                document_id,
                store
            )
        except Exception as e:
            print(
                f"Failed: {document_id}"
            )
            print(e)

    end = time.perf_counter()

    print(
        f"Processed "
        f"{len(document_ids)} docs "
        f"in "
        f"{end - start:.2f}s"
    )

    await pool.close()


if __name__ == "__main__":

    ids = input(
        "Comma separated document ids: "
    )

    asyncio.run(
        benchmark(
            [
                x.strip()
                for x in ids.split(",")
            ]
        )
    )