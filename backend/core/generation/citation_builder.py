from collections import defaultdict

from core.generation.schemas import Citation


def build_citations(chunks: list[dict]) -> list[Citation]:
    """
    Build structured citations from retrieved chunks.

    Chunks belonging to the same document are merged into
    a single citation.

    PDF documents contribute page numbers.

    Non-paginated documents (DOCX, TXT, MD) contribute
    section references based on chunk index.
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
                "section_references": set(),
                "chunk_indexes": set(),
                "department_id": chunk.get("department_id"),
                "chunk_excerpt": excerpt,
            }

        #
        # PDF page reference
        #
        page_number = chunk.get("page_number")

        if page_number is not None and page_number >= 0:

            grouped[document_name]["page_numbers"].add(
                page_number
            )

         #
        # DOCX / TXT / MD section reference
        #
        else:

            chunk_index = chunk.get("chunk_index")

            if chunk_index is not None:

                grouped[document_name][
                    "section_references"
                ].add(
                    f"Section {chunk_index + 1}"
                )

        chunk_index = chunk.get("chunk_index")

        if chunk_index is not None:
            grouped[document_name]["chunk_indexes"].add(chunk_index)

    citations = []

    for citation in grouped.values():

        citations.append(
            Citation(
                document_name=citation["document_name"],
                page_numbers=sorted(citation["page_numbers"]),
                section_references=sorted(citation["section_references"]),
                chunk_indexes=sorted(citation["chunk_indexes"]),
                department_id=citation["department_id"],
                chunk_excerpt=citation["chunk_excerpt"],
            )
        )

    return citations