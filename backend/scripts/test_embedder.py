from core.retrieval.embedder import Embedder


def main():

    embedder = Embedder.get_instance()

    embedding = embedder.embed(
        [
            "Employee annual leave policy"
        ]
    )

    print(
        "Vector count:",
        len(embedding)
    )

    print(
        "Dimension:",
        len(embedding[0])
    )


if __name__ == "__main__":
    main()