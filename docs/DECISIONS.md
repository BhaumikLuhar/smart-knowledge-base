# Engineering Decisions

## Day 1

### Stack Selection

Frontend:
- Next.js
- Tailwind
- shadcn/ui

Backend:
- FastAPI

Database:
- PostgreSQL (Supabase)

Vector Database:
- Chroma

Reason:
Chosen for rapid development, strong ecosystem support, and clear separation between structured data and vector search.


## Day 2 - Database Schema Decisions


### Why department_id is duplicated on chunks

Chunks inherit department_id from their parent document.

This allows fast permission filtering during retrieval without requiring joins back to the documents table for every query.

### Why visibility is copied to chunks

Visibility rules are enforced at retrieval time.

Duplicating visibility on chunks allows vector and keyword retrieval systems to filter directly on chunk metadata instead of fetching document metadata separately.