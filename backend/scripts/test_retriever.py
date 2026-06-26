import asyncio

from core.database import create_db_pool
from core.auth.user_context import UserContext

from storage.sql.sql_store import SQLStore

from core.retrieval.vector_retriever import (
    VectorRetriever
)

from core.retrieval.bm25_retriever import (
    BM25Retriever
)

from core.retrieval.hybrid_retriever import (
    HybridRetriever
)

from core.retrieval.registry import (
    get_retriever
)


async def build_test_user(
    sql_store: SQLStore
) -> UserContext:
    """
    Use first non-admin user.

    Adjust later if needed.
    """

    users = await sql_store.query(
        "users",
        {},
        limit=10
    )

    for user in users:

        if user["role"] != "admin":

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

    raise Exception(
        "No non-admin user found"
    )


async def print_results(
    title: str,
    results: list[dict]
):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    for result in results[:5]:

        print(
            result
        )


async def main():

    pool = await create_db_pool()

    try:

        sql_store = SQLStore(pool)

        user = await build_test_user(
            sql_store
        )

        query = input(
            "Query: "
        )

        print()
        print(
            f"Testing as "
            f"{user.email}"
        )

        #
        # Vector
        #

        vector = VectorRetriever(
            sql_store
        )

        vector_results = (
            await vector.retrieve(
                query,
                user
            )
        )

        await print_results(
            "VECTOR RESULTS",
            vector_results
        )

        #
        # BM25
        #

        bm25 = BM25Retriever(
            sql_store
        )

        bm25_results = (
            await bm25.retrieve(
                query,
                user
            )
        )

        await print_results(
            "BM25 RESULTS",
            bm25_results
        )

        #
        # Hybrid
        #

        hybrid = HybridRetriever(
            sql_store
        )

        hybrid_results = (
            await hybrid.retrieve(
                query,
                user
            )
        )

        await print_results(
            "HYBRID RESULTS",
            hybrid_results
        )

        #
        # Registry
        #

        registry_retriever = (
            get_retriever(
                sql_store
            )
        )

        registry_results = (
            await registry_retriever.retrieve(
                query,
                user
            )
        )

        await print_results(
            "REGISTRY RESULTS",
            registry_results
        )

    finally:

        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())