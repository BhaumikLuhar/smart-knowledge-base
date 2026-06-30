import asyncio
import asyncpg

from core.config import settings
from storage.sql.sql_store import SQLStore


TEST_DEPARTMENT = {
    "name": "test_department",
    "display_name": "Test Department",
    "description": "Created by SQLStore test"
}


async def run_test():

    pool = await asyncpg.create_pool(
        settings.DATABASE_URL,ssl="require",statement_cache_size=0,
    )

    store = SQLStore(pool)

    try:

        print("\n==========")
        print("TEST SAVE")
        print("==========")

        created = await store.save(
            "departments",
            TEST_DEPARTMENT
        )

        print(created)

        department_id = created["id"]

        print("\n==========")
        print("TEST QUERY")
        print("==========")

        rows = await store.query(
            "departments",
            filters={
                "name": "test_department"
            }
        )

        print(rows)

        print("\n==========")
        print("TEST UPDATE")
        print("==========")

        updated = await store.update(
            "departments",
            department_id,
            {
                "display_name": "Updated Department"
            }
        )

        print(updated)

        print("\n==========")
        print("TEST EXECUTE_RAW")
        print("==========")

        result = await store.execute_raw(
            """
            SELECT
                id,
                name,
                display_name
            FROM departments
            WHERE id = $1
            """,
            (department_id,)
        )

        print(result)

        print("\n==========")
        print("TEST DELETE")
        print("==========")

        deleted = await store.delete(
            "departments",
            department_id
        )

        print(
            f"Deleted: {deleted}"
        )

        remaining = await store.query(
            "departments",
            filters={
                "id": department_id
            }
        )

        print(
            f"Rows after delete: {len(remaining)}"
        )

        print("\n🎉 ALL TESTS PASSED")

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(run_test())