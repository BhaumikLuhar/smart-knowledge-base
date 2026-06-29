import asyncio

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore
from core.observability.metrics import MetricsRecorder


async def main():

    pool = await create_db_pool()

    store = SQLStore(pool)

    recorder = MetricsRecorder(store)

    await recorder.record_success(
        endpoint="/test",
        user_id="edbf7259-9ac7-4c71-9ee9-afdfd682b4b7",
        latency=123.5,
        tokens=88,
        retrieval_count=5,
    )

    print("Metric inserted.")

    await pool.close()


asyncio.run(main())