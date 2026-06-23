# Architecture

## Current Architecture

Frontend (Next.js)

↓

FastAPI Backend

↓

Knowledge Layer

↓

Storage Layer

(PostgreSQL + Chroma)

## Notes

This document will be expanded as features are implemented.

## Retrieval Pipeline

Upload
→ Parse
→ Chunk
→ PostgreSQL Storage
→ Embedding Generation
→ Chroma Vector Storage

Each chunk receives:

- PostgreSQL chunk ID
- Chroma vector ID (same value)
- embedding_ref

This enables direct cross-referencing between relational and vector stores.

### Future Permission Enforcement

Day 10 introduces department pre-filtering using Chroma metadata filters.

Example:

{
  "department_id": {
    "$in": ["hr", "engineering"]
  }
}

This acts as the first retrieval-layer permission filter before the permission engine performs final authorization checks.