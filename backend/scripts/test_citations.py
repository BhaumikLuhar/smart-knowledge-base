from core.generation.citation_builder import build_citations

chunks = [
    {
        "document_name": "Employee Handbook",
        "page_number": 4,
        "section_reference": "Section 2.1",
        "chunk_index": 2,
        "department_id": "hr",
        "text": "Annual leave policy " * 20,
    },
    {
        "document_name": "Employee Handbook",
        "page_number": 7,
        "section_reference": "Section 2.1",
        "chunk_index": 5,
        "department_id": "hr",
        "text": "Another section",
    },
    {
        "document_name": "Security Policy",
        "page_number": 1,
        "section_reference": "Section 2.1",
        "chunk_index": 0,
        "department_id": "it",
        "text": "Security rules",
    },
]

citations = build_citations(chunks)

for citation in citations:
    print(citation.model_dump())