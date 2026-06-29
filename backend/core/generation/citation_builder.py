from collections import defaultdict

from core.generation.schemas import Citation


def build_citations(chunks: list[dict]) -> list[Citation]:
    """
    Build citations from retrieved chunks.

    Multiple chunks from the same document are merged
    into a single citation while preserving every
    referenced page and chunk index.
    """

    if not chunks:
        return []

    grouped: dict[str, dict] = defaultdict(dict)

    for chunk in chunks:

        document_name = chunk["document_name"]

        if document_name not in grouped:

            excerpt = chunk["text"]

            if len(excerpt) > 200:
                excerpt = excerpt[:200] + "..."

            grouped[document_name] = {
                "document_name": document_name,
                "page_numbers": set(),
                "chunk_indexes": set(),
                "department_id": chunk.get("department_id"),
                "chunk_excerpt": excerpt,
            }

        #
        # Ignore unknown page numbers (-1)
        #
        page = chunk.get("page_number")

        if page is not None and page >= 0:
            grouped[document_name]["page_numbers"].add(page)

        chunk_index = chunk.get("chunk_index")

        if chunk_index is not None:
            grouped[document_name]["chunk_indexes"].add(chunk_index)

    citations = []

    for citation in grouped.values():

        citations.append(
            Citation(
                document_name=citation["document_name"],
                page_numbers=sorted(citation["page_numbers"]),
                chunk_indexes=sorted(citation["chunk_indexes"]),
                department_id=citation["department_id"],
                chunk_excerpt=citation["chunk_excerpt"],
            )
        )

    return citations