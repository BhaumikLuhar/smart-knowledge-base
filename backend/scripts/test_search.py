from core.retrieval.embedder import Embedder
from storage.vector.vector_store import VectorStore


def main():

    query = (
        "What is the employee leave policy?"
    )

    embedder = Embedder.get_instance()

    vector_store = (
        VectorStore.get_instance()
    )

    query_embedding = (
        embedder.embed_query(query)
    )

    results = vector_store.query(
        query_embedding=query_embedding,
        top_k=3,
        where={
            "department_id":
            "e566be91-232c-49c5-b1fa-cabff29b38f1"
        }
    )

    print("\n")
    print("=" * 80)
    print("QUERY")
    print("=" * 80)
    print(query)

    print("\n")
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    for i, doc in enumerate(documents):

        print("\n")
        print(f"Result #{i+1}")

        print(
            f"Distance: "
            f"{distances[i]}"
        )

        print(
            f"Metadata: "
            f"{metadatas[i]}"
        )

        print("\nChunk:")
        print(doc[:500])

        print("\n" + "-" * 80)


if __name__ == "__main__":
    main()