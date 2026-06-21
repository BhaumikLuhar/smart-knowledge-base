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