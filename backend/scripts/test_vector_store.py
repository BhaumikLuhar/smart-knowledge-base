from storage.vector.vector_store import VectorStore


def main():

    store = VectorStore.get_instance()

    print(
        "Collection count:",
        store.count()
    )


if __name__ == "__main__":
    main()