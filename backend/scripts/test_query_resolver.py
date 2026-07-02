from core.conversation.query_resolver import QueryResolver

def run_case(
    resolver: QueryResolver,
    title: str,
    query: str,
    history: list[dict],
):
    print("=" * 80)
    print(title)
    print("-" * 80)
    print("Original Query:")
    print(query)

    print("\nHistory:")
    if not history:
        print("(empty)")
    else:
        for message in history:
            print(f"{message['role']:>10}: {message['content']}")

    resolved = resolver.resolve(
        query=query,
        history=history,
    )

    print("\nResolved Query:")
    print(resolved)
    print()


def main():

    resolver = QueryResolver()

    #
    # Case 1
    # Standalone query
    #
    run_case(
        resolver,
        "CASE 1 - Standalone Question",
        "What is onboarding?",
        [],
    )

    #
    # Case 2
    # Pronoun resolution
    #
    history = [
        {
            "role": "user",
            "content": "What is the leave policy?",
        },
        {
            "role": "assistant",
            "content": (
                "Employees receive 20 annual paid leaves, "
                "12 sick leaves and 10 public holidays."
            ),
        },
    ]

    run_case(
        resolver,
        "CASE 2 - Pronoun Resolution",
        "How many days is that?",
        history,
    )

    #
    # Case 3
    #
    run_case(
        resolver,
        "CASE 3 - 'it' reference",
        "Explain it.",
        history,
    )

    #
    # Case 4
    #
    run_case(
        resolver,
        "CASE 4 - 'those' reference",
        "Can those be carried forward?",
        history,
    )

    #
    # Case 5
    #
    onboarding_history = [
        {
            "role": "user",
            "content": "What is onboarding?",
        },
        {
            "role": "assistant",
            "content": (
                "Onboarding is the employee orientation "
                "process that takes one to two weeks."
            ),
        },
    ]

    run_case(
        resolver,
        "CASE 5 - Different Topic",
        "How long does it take?",
        onboarding_history,
    )


if __name__ == "__main__":
    main()