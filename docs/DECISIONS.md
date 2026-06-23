# Engineering Decisions

## Day 1

### Stack Selection

**Frontend**
- Next.js
- Tailwind CSS
- shadcn/ui

**Backend**
- FastAPI

**Database**
- PostgreSQL (Supabase)

**Vector Database**
- Chroma

**Reason**

Chosen for rapid development, strong ecosystem support, and clear separation between structured data and vector search.

---

## Day 2

### Database Schema Decisions

#### Why `department_id` is duplicated on chunks

Chunks inherit `department_id` from their parent document.

This allows fast permission filtering during retrieval without requiring joins back to the documents table for every query.

#### Why `visibility` is copied to chunks

Visibility rules are enforced at retrieval time.

Duplicating visibility on chunks allows vector and keyword retrieval systems to filter directly on chunk metadata instead of fetching document metadata separately.

#### ADR-003: Use Supabase Transaction Pooler Instead of Direct Connection

**Context**

Direct Supabase PostgreSQL connections were producing connection issues during development.

**Decision**

Use the Supabase Transaction Pooler connection string with:

```python
ssl="require"
```

inside asyncpg connection pool creation.

**Consequences**
- More stable connection handling
- Better compatibility with Supabase infrastructure
- Future services should continue using pooled connections through `create_db_pool()`

---

## Day 3

### Upload Pipeline and Loader Registry

#### ADR-004: Store Uploaded Documents on Local Disk Before Ingestion

**Context**

The execution plan requires documents to be uploaded and registered before chunking and embedding are implemented.

**Decision**

Store uploaded files in:

```text
storage/files/{department_name}/
```

using UUID-prefixed filenames.

Example:

```text
storage/files/engineering/{uuid}_employee_handbook.pdf
```

**Consequences**
- Original files remain available for re-processing
- Future ingestion jobs can re-run without requiring re-upload
- Document versioning becomes easier

---

#### ADR-005: Resolve Upload Paths Using Project Root

**Context**

Using:

```python
UPLOAD_DIR = "./backend/storage/files"
```

caused files to be stored inside:

```text
backend/backend/storage/files
```

when Uvicorn was launched from the backend directory.

**Decision**

Resolve upload directories from the project root instead of relative paths.

**Consequences**
- Upload location is independent of working directory
- Prevents accidental nested folder creation
- Future storage locations should also use root-based paths

---

#### ADR-006: Centralize JSONB Serialization in SQLStore

**Context**

PostgreSQL JSONB inserts failed with:

```text
expected str, got dict
```

when inserting metadata.

**Decision**

Serialize Python `dict` and `list` values inside `SQLStore.save()` before database insertion.

**Consequences**
- All services can store JSONB fields consistently
- Avoids repeated serialization logic in business services
- Supports future metadata, audit logs, and retrieval traces

---

#### ADR-007: Use Database Defaults for Timestamps

**Context**

Application-generated UTC timestamps caused timezone compatibility issues with PostgreSQL timestamp columns.

**Decision**

Allow PostgreSQL defaults to populate:

- `created_at`
- `updated_at`

instead of manually setting them during inserts.

**Consequences**
- Consistent timestamp generation
- Simpler service layer
- Fewer timezone-related bugs


## Day 4 - Metadata Storage

Document metadata is stored in PostgreSQL JSONB.

Reasoning:

- Flexible schema evolution
- No migration required for future metadata fields
- Efficient querying through PostgreSQL JSON operators
- Same structure can be propagated into chunk metadata

Structure:

{
  description,
  tags,
  author,
  effective_date,
  expiry_date,
  custom
}


## Day 4 - Soft Delete Strategy

Documents are not physically deleted.

Instead:

status = 'deleted'

Reasoning:

- Prevent accidental data loss
- Simplifies recovery
- Avoids orphaned vector references
- Allows future cleanup jobs


## Day 5 - Document Ingestion Pipeline

Implemented document ingestion that converts uploaded documents into searchable text chunks stored in PostgreSQL.

Reasoning:

- Sentence-aware chunking improves retrieval quality
- Background processing prevents upload requests from blocking
- Chunk persistence enables validation before embeddings
- Bulk inserts reduce database overhead
- Failure tracking simplifies troubleshooting

Configuration:

```text
Chunk Size: 800 characters
Overlap: 100 characters
```

Workflow:

```text
Upload
→ pending
→ processing
→ chunk generation
→ chunk persistence
→ ready
```

Stored Chunk Fields:

```text
document_id
department_id
visibility
chunk_index
text
page_number
```

Current behavior:

```text
page_number = null
```

---

## Day 5 - Error Handling

Documents that produce no extractable text are not ingested.

Current behavior:

```text
status = 'failed'
metadata.ingestion_error
```

Reasoning:

- Prevents ingestion crashes
- Provides clear failure diagnostics
- Supports future retry workflows

---

## Day 5 - File Path Strategy

Uploaded document paths are stored as absolute filesystem paths.

Reasoning:

- Prevents path resolution issues
- Works consistently across background tasks
- Independent of current working directory

---

### Validation Results

Verified:

- Upload → Pending → Processing → Ready workflow
- Background ingestion execution
- Chunk creation
- Multi-row database insertion
- Audit log generation
- Failure handling for invalid documents
- UI polling updates
- Processing indicators in frontend

---

### Day 5 Outcome

The system can now:

- Upload documents
- Parse content
- Generate chunks
- Persist chunks
- Track ingestion state
- Recover from ingestion failures


## Day 6 – Embedding Model Selection

### Decision
Selected BAAI/bge-small-en-v1.5 as the embedding model.

### Rationale
- Strong retrieval performance for RAG workloads
- Lightweight compared to larger embedding models
- 384-dimensional vectors reduce storage requirements
- Fast inference on CPU
- Open-source and local execution

### Query Embedding Strategy
Document chunks are embedded directly.

User queries are embedded using the BGE recommended prefix:

Represent this sentence for searching relevant passages:

This improves retrieval quality for semantic search.


---

## Day 6 - Chroma Metadata Filtering Strategy

### ADR-008: Store Permission-Relevant Metadata in Chroma

**Context**

Week 2 introduces permission-aware retrieval.

During semantic search, the system must restrict results before they reach the application layer.

Performing permission filtering after retrieval would:

* Increase unnecessary vector search results
* Waste retrieval bandwidth
* Increase latency
* Complicate authorization logic

### Decision

Store permission-relevant metadata directly inside Chroma for every chunk.

Current metadata structure:

```python
{
    "document_id": "...",
    "chunk_id": "...",
    "department_id": "...",
    "visibility": "...",
    "document_name": "...",
    "chunk_index": 0,
    "page_number": -1
}
```

### Current Usage

Department-restricted retrieval:

```python
where = {
    "department_id": department_id
}
```

### Consequences

Benefits:

* Fast pre-filtering during vector search
* Reduced retrieval noise
* Lower latency
* Cleaner permission implementation

Tradeoffs:

* Metadata duplicated between PostgreSQL and Chroma
* Additional storage overhead

This duplication is accepted because retrieval performance is prioritized over storage efficiency.

---

## Day 6 - Shared Identifier Strategy

### ADR-009: Use Chunk UUID as Both SQL and Vector Identifier

**Context**

Each chunk exists in two systems:

1. PostgreSQL
2. Chroma

A reliable mapping between systems is required.

### Decision

Generate a UUID during chunk creation.

Use the same UUID as:

* chunks.id
* Chroma vector id
* chunks.embedding_ref

Example:

```text
Chunk ID:
dee745ed-376b-43e4-96d1-11763fdc24dc

PostgreSQL:
chunks.id

Chroma:
vector id

Reference:
embedding_ref
```

### Consequences

Benefits:

* Direct cross-system lookup
* Simplified debugging
* Easier future deletion workflows
* Easier re-indexing

Tradeoffs:

* Requires UUID generation before persistence

This tradeoff is acceptable.

---

## Day 6 - Singleton Resource Strategy

### ADR-010: Use Singleton Pattern for Heavy Retrieval Components

**Context**

Loading embedding models and vector database connections repeatedly would significantly increase:

* Startup time
* Memory usage
* Request latency

### Decision

Use singleton instances for:

#### Embedder

```python
Embedder.get_instance()
```

#### VectorStore

```python
VectorStore.get_instance()
```

### Consequences

Benefits:

* Embedding model loaded once
* Reduced memory consumption
* Faster ingestion
* Faster retrieval

Tradeoffs:

* Shared application state
* More care required during testing

For the current architecture, benefits outweigh drawbacks.

---

## Day 7 - Storage Boundary Enforcement

### ADR-011: Enforce Storage Layer Isolation

**Context**

The system uses:

* PostgreSQL
* Chroma

Without architectural boundaries, business services can become tightly coupled to infrastructure implementations.

This makes future replacement of storage technologies difficult.

### Decision

Knowledge services and retrieval services must never directly import:

```python
asyncpg
chromadb
```

Allowed architecture:

```text
Knowledge Layer
        ↓
Storage Layer
        ↓
Database
```

Examples:

```python
from storage.sql.sql_store import SQLStore

from storage.vector.vector_store import VectorStore
```

### Consequences

Benefits:

* Cleaner architecture
* Easier testing
* Easier refactoring
* Future vector database replacement
* Future database replacement

Tradeoffs:

* Additional abstraction layer

This tradeoff is accepted.

---

## Day 7 - Background Ingestion Strategy

### ADR-012: Use FastAPI BackgroundTasks for Initial Ingestion

**Context**

Document ingestion involves:

* Parsing
* Chunking
* Embedding generation
* Vector persistence

Running these operations during the upload request would significantly increase response time.

### Decision

Use FastAPI BackgroundTasks to execute ingestion asynchronously.

Workflow:

```text
Upload Request
        ↓
Document Registration
        ↓
HTTP Response
        ↓
Background Ingestion
```

### Consequences

Benefits:

* Fast upload response
* Better user experience
* Simpler implementation

Tradeoffs:

* Tasks are process-local
* Server restart may interrupt ingestion

This limitation is acceptable for Week 1.

Future phases may replace this with:

* Celery
* RQ
* Dramatiq
* Dedicated worker services

---

## Week 1 Summary

At the end of Week 1 the system supports:

* Department management
* Document upload
* Metadata storage
* Loader registry
* Background ingestion
* Chunk generation
* PostgreSQL chunk persistence
* Embedding generation
* Chroma vector persistence
* Semantic search
* Department-level filtering
* Administrative Knowledge Base UI
* Status polling
* Audit logging

Week 2 introduces:

* Authentication
* Permission enforcement
* Session management
* Secure retrieval
* User-aware search