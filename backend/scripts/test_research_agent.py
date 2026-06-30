import asyncio

from agents.workflow import run_agent_pipeline

from core.auth.user_context import UserContext
from core.retrieval.retrieval_pipeline import RetrievalPipeline

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore


# =====================================================
# Test Users
# =====================================================

HR_USER = UserContext(
    id="88c59970-9bdd-45bb-adfd-6afa3cd53528",
    email="hr@skb.com",
    role="employee",
    department_id="08785eea-78c7-4826-93fb-d69c23d174b7",
    is_active=True,
)

#
# Replace with your Engineering user
#
ENGINEERING_USER = UserContext(
    id="edbf7259-9ac7-4c71-9ee9-afdfd682b4b7",
    email="engineering@skb.com",
    role="employee",
    department_id="e566be91-232c-49c5-b1fa-cabff29b38f1",
    is_active=True,
)


# =====================================================
# Helpers
# =====================================================

TOTAL_TESTS = 0
PASSED_TESTS = 0


def check(condition: bool, message: str):
    global TOTAL_TESTS
    global PASSED_TESTS

    TOTAL_TESTS += 1

    if condition:
        PASSED_TESTS += 1
        print(f"[PASS] {message}")
    else:
        print(f"[FAIL] {message}")


def print_header(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# =====================================================
# Tests
# =====================================================

async def test_hr_user(pipeline: RetrievalPipeline):

    print_header("TEST 1 - HR USER")

    state = await run_agent_pipeline(
        query="What is the leave policy?",
        user_context=HR_USER,
        session_id="research-test",
        pipeline=pipeline,
    )

    #
    # Planner
    #
    check(
        len(state["search_queries"]) > 0,
        "Planner produced search queries",
    )

    #
    # Research
    #
    check(
        len(state["retrieved_chunks"]) > 0,
        "Research retrieved chunks",
    )

    #
    # no_results
    #
    check(
        state["no_results"] is False,
        "no_results correctly False",
    )

    #
    # FINAL_TOP_K
    #
    check(
        len(state["retrieved_chunks"]) <= 5,
        "FINAL_TOP_K respected",
    )

    #
    # Trace
    #
    research_trace = [
        t
        for t in state["trace"]
        if t["agent_name"] == "research"
    ]

    check(
        len(research_trace) == 1,
        "Research trace added",
    )

    #
    # Deduplication
    #
    chunk_ids = [
        chunk["chunk_id"]
        for chunk in state["retrieved_chunks"]
    ]

    check(
        len(chunk_ids) == len(set(chunk_ids)),
        "Duplicate chunks removed",
    )

    #
    # Sorted by rerank score
    #
    scores = [
        chunk.get("rerank_score", 0)
        for chunk in state["retrieved_chunks"]
    ]

    check(
        scores == sorted(scores, reverse=True),
        "Chunks sorted by rerank score",
    )

    #
    # Debug output
    #
    print("\nRetrieved Chunks")

    for chunk in state["retrieved_chunks"]:

        print(
            f"{chunk['document_name']}"
            f" | rerank={chunk['rerank_score']:.3f}"
            f" | hybrid={chunk['hybrid_score']:.3f}"
        )


async def test_engineering_user(
    pipeline: RetrievalPipeline,
):

    print_header("TEST 2 - ENGINEERING USER")

    state = await run_agent_pipeline(
        query="What is the leave policy?",
        user_context=ENGINEERING_USER,
        session_id="research-test",
        pipeline=pipeline,
    )

    #
    # Engineering should not receive HR chunks.
    #
    check(
        state["no_results"],
        "Engineering user blocked from HR content",
    )

    check(
        len(state["retrieved_chunks"]) == 0,
        "No chunks returned",
    )


async def test_multi_query_dedup(
    pipeline: RetrievalPipeline,
):

    print_header("TEST 3 - MULTI QUERY DEDUP")

    state = await run_agent_pipeline(
        query="Summarize employee leave policy",
        user_context=HR_USER,
        session_id="research-test",
        pipeline=pipeline,
    )

    chunk_ids = [
        chunk["chunk_id"]
        for chunk in state["retrieved_chunks"]
    ]

    check(
        len(chunk_ids) == len(set(chunk_ids)),
        "Multi-query deduplication successful",
    )

    print("\nPlanner Queries")

    for q in state["search_queries"]:
        print("-", q)


# =====================================================
# Main
# =====================================================

async def main():

    print_header("DAY 16 RESEARCH AGENT VALIDATION")

    pool = await create_db_pool()

    sql_store = SQLStore(pool)

    pipeline = RetrievalPipeline(sql_store)

    try:

        await test_hr_user(pipeline)

        await test_engineering_user(pipeline)

        await test_multi_query_dedup(pipeline)

    finally:

        await pool.close()

    print_header("SUMMARY")

    print(
        f"Passed: {PASSED_TESTS}/{TOTAL_TESTS}"
    )

    if PASSED_TESTS == TOTAL_TESTS:
        print("\n🎉 DAY 16 VALIDATION PASSED")
    else:
        print("\n SOME TESTS FAILED")


if __name__ == "__main__":
    asyncio.run(main())