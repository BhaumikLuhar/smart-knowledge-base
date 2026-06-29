import asyncio
import time

from core.database import create_db_pool
from core.auth.user_context import UserContext
from core.retrieval.retrieval_pipeline import RetrievalPipeline
from core.config import settings

from storage.sql.sql_store import SQLStore


async def get_department_map(sql_store: SQLStore) -> dict:
    departments = await sql_store.query("departments")

    return {
        str(dept["id"]): dept["name"]
        for dept in departments
    }


async def get_user(
    sql_store: SQLStore,
    email: str
) -> UserContext:
    """
    Load a user by email and build a UserContext.
    """

    users = await sql_store.query(
        "users",
        {
            "email": email
        }
    )

    if not users:
        raise Exception(f"User '{email}' not found.")

    user = users[0]

    return UserContext(
        id=str(user["id"]),
        email=user["email"],
        role=user["role"],
        department_id=(
            str(user["department_id"])
            if user["department_id"]
            else None
        ),
        is_active=user["is_active"]
    )


async def print_result(
    title: str,
    result: dict,
    sql_store: SQLStore
):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(f"Query               : {result['query']}")
    print(f"Candidates          : {result['candidate_count']}")
    print(f"Authorized          : {result['authorized_count']}")
    filtered = (
        result["candidate_count"]
        - result["authorized_count"]
    )
    print(f"Filtered            : {filtered}")
    print(f"Returned            : {len(result['chunks'])}")

    if result.get("message"):
        print(f"Message             : {result['message']}")

    print()

    for i, chunk in enumerate(result["chunks"], start=1):

        print(f"[{i}]")

        print(
            f"Document     : "
            f"{chunk['document_name']}"
        )
        department_map = await get_department_map(sql_store)

        print(
            department_map.get(
                chunk["department_id"],
                chunk["department_id"]
            )
        )
        print(
            f"Department   : "
            f"{chunk['department_id']}"
        )

        print(
            f"Visibility   : "
            f"{chunk['visibility']}"
        )

        print(
            f"Score        : "
            f"{chunk['score']:.4f}"
        )

        print(
            f"Text         : "
            f"{chunk['text'][:150]}..."
        )

        print("-" * 80)

        print(
            chunk
        )

        print("-" * 80)


async def verify_audit_log(
    sql_store: SQLStore
):
    """
    Print the latest query audit log.
    """

    rows = await sql_store.query(
        "audit_logs",
        {
            "action": "query"
        },
        order_by="created_at DESC",
        limit=1
    )

    if not rows:
        print("\nNo audit log found.")
        return

    print()
    print("=" * 80)
    print("LATEST AUDIT LOG")
    print("=" * 80)

    print(rows[0])


async def main():

    pool = await create_db_pool()

    try:

        sql_store = SQLStore(pool)

        pipeline = RetrievalPipeline(
            sql_store
        )
        print("=" * 80)
        print("DAY 12 RERANKER BENCHMARK")
        print("=" * 80)

        print(
            f"Reranker : {settings.RERANKER_TYPE}"
        )

        if settings.RERANKER_TYPE == "cross_encoder":
            print(
                f"Model    : "
                f"{settings.CROSS_ENCODER_MODEL}"
            )

        print("=" * 80)

        engineering_user = await get_user(
            sql_store,
            "user1@skb.com"
        )

        hr_user = await get_user(
            sql_store,
            "hr@skb.com"
        )

        #
        # Scenario 1
        #

        start = time.perf_counter()

        hr_leave = await pipeline.retrieve_and_filter(
            "leave policy",
            hr_user
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"\nRetrieval latency: "
            f"{elapsed_ms:.2f} ms"
        )

        assert (
            len(hr_leave["chunks"])
            <= hr_leave["authorized_count"]
        )

        await print_result(
            "SCENARIO 1 - HR USER - LEAVE POLICY",
            hr_leave,
            sql_store
        )

        await verify_audit_log(sql_store)

        assert all(
            chunk["department_id"] != engineering_user.department_id
            for chunk in hr_leave["chunks"]
        ), "HR user received Engineering chunks!"

        # #
        # # Scenario 2
        # #
        # start = time.perf_counter()

        # engineering_leave = await pipeline.retrieve_and_filter(
        #     "leave policy",
        #     engineering_user
        # )
    
        # elapsed_ms = (
        #     time.perf_counter() - start
        # ) * 1000

        # print(
        #     f"\nRetrieval latency: "
        #     f"{elapsed_ms:.2f} ms"
        # )

        # assert (
        #     len(hr_leave["chunks"])
        #     <= hr_leave["authorized_count"]
        # )

        # await print_result(
        #     "SCENARIO 2 - ENGINEERING USER - LEAVE POLICY",
        #     engineering_leave,
        #     sql_store
        # )

        # await verify_audit_log(sql_store)

        # #
        # # Scenario 3
        # #
        # start = time.perf_counter()

        # engineering_deployment = await pipeline.retrieve_and_filter(
        #     "deployment process",
        #     engineering_user
        # )
    
        # elapsed_ms = (
        #     time.perf_counter() - start
        # ) * 1000

        # print(
        #     f"\nRetrieval latency: "
        #     f"{elapsed_ms:.2f} ms"
        # )

        # assert (
        #     len(hr_leave["chunks"])
        #     <= hr_leave["authorized_count"]
        # )

        # await print_result(
        #     "SCENARIO 3 - ENGINEERING USER - DEPLOYMENT",
        #     engineering_deployment,
        #     sql_store
        # )

        # await verify_audit_log(sql_store)

        # assert all(
        #     chunk["department_id"] != hr_user.department_id
        #     for chunk in engineering_deployment["chunks"]
        # ), "Engineering user received HR chunks!"

        # #
        # # Scenario 4
        # #
        # start = time.perf_counter()

        # hr_deployment = await pipeline.retrieve_and_filter(
        #     "deployment process",
        #     hr_user
        # )

        # elapsed_ms = (
        #     time.perf_counter() - start
        # ) * 1000

        # print(
        #     f"\nRetrieval latency: "
        #     f"{elapsed_ms:.2f} ms"
        # )

        # assert (
        #     len(hr_leave["chunks"])
        #     <= hr_leave["authorized_count"]
        # )

        # await print_result(
        #     "SCENARIO 4 - HR USER - DEPLOYMENT",
        #     hr_deployment,
        #     sql_store
        # )

        # await verify_audit_log(sql_store)

    finally:

        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())