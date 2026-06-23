import asyncio
from uuid import uuid4

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore


async def main():

    pool = await create_db_pool()

    store = SQLStore(pool)

    document_id = input(
        "Document UUID: "
    )

    department_id = input(
        "Department UUID: "
    )

    chunks = []

    for i in range(3):

        chunks.append(
            {
                "id": str(uuid4()),
                "document_id": document_id,
                "text": f"Test chunk {i}",
                "chunk_index": i,
                "page_number": None,
                "department_id": department_id,
                "visibility": "department"
            }
        )

    inserted = await store.bulk_insert_chunks(
        chunks
    )

    print(
        f"Inserted {inserted} chunks"
    )

    await pool.close()


asyncio.run(main())