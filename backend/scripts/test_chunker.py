from core.knowledge.chunker import chunk_text


sample_text = """
Smart Knowledge Bank is an enterprise platform.

It allows organizations to upload documents.

Employees can search for information.

Permission filtering ensures users only access authorized data.

Chunking improves retrieval quality.

Embeddings will be added on Day 6.
""" * 5


chunks = chunk_text(
    text=sample_text,
    doc_id="doc-1",
    dept_id="dept-1",
    visibility="department"
)

print(f"Chunks created: {len(chunks)}")

for chunk in chunks:
    print("\n" + "=" * 50)
    print(chunk["chunk_index"])
    print(chunk["text"])