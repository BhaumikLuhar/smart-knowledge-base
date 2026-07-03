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


## Day 8 - Authentication Architecture

### ADR-011: JWT-Based Authentication

**Context**

The Day 3 implementation used a temporary administrative header:

```http
X-Admin-Token: dev-token
```

This approach was sufficient during initial development but provided:

* No user identity
* No role awareness
* No department awareness
* No session tracking
* No scalable authorization model

Week 2 introduces role-based permissions and department-aware retrieval, requiring a proper authentication layer.

### Decision

Implement stateless JWT authentication.

Each authenticated user receives a signed JWT containing:

```json
{
    "sub": "user_id",
    "email": "user@example.com",
    "role": "employee",
    "department_id": "department_uuid",
    "exp": "expiration_timestamp"
}
```

JWT configuration:

```python
JWT_SECRET
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 480
```

Authentication flow:

```text
Login
    ↓
Verify password
    ↓
Generate JWT
    ↓
Return token
    ↓
Frontend stores token
    ↓
Authorization: Bearer <token>
```

### Consequences

Benefits:

* Stateless authentication
* Horizontal scalability
* Role-aware authorization
* Department-aware authorization
* Compatible with future API consumers and agents

Tradeoffs:

* Token revocation requires additional infrastructure
* Logout cannot immediately invalidate issued tokens

Future enhancement:

* Refresh tokens
* Token blacklist
* Token rotation


## Day 8 - Authentication Context Strategy

### ADR-012: UserContext Dependency Pattern

**Context**

Most application services require access to the currently authenticated user.

Examples:

* Document uploads
* Permission evaluation
* Retrieval filtering
* Audit logging
* Future chat sessions

Passing user information manually through endpoints would introduce duplication and increase maintenance complexity.

### Decision

Introduce a centralized authentication dependency:

```python
get_current_user()
```

The dependency:

1. Extracts JWT from the Authorization header
2. Verifies signature and expiration
3. Loads the user from PostgreSQL
4. Validates account status
5. Returns a UserContext object

```python
UserContext(
    id,
    email,
    role,
    department_id,
    is_active
)
```

Administrative endpoints use:

```python
require_admin()
```

which extends authentication with role validation.

### Consequences

Benefits:

* Centralized authentication logic
* Consistent authorization enforcement
* Reduced code duplication
* Easier future permission integration

Tradeoffs:

* Additional database lookup per authenticated request

This tradeoff is accepted because user status and permissions must remain authoritative in PostgreSQL.


## Day 8 - Frontend Authentication Strategy

### ADR-013: localStorage Token Storage for MVP

**Context**

The frontend requires persistent authentication across:

* Page refreshes
* Browser navigation
* Dashboard sessions

Two implementation options were evaluated:

1. localStorage
2. httpOnly cookies

### Decision

Store JWTs in localStorage during MVP development.

Frontend authentication state is managed through:

```text
AuthContext
```

Persisted values:

```text
access_token
user
```

Authentication flow:

```text
Login
    ↓
Store token
    ↓
Store user profile
    ↓
AuthContext hydration
    ↓
Protected layouts
```

### Consequences

Benefits:

* Fast implementation
* Simple React integration
* Minimal backend complexity
* Compatible with existing architecture

Tradeoffs:

* Vulnerable to XSS if frontend is compromised
* Middleware cannot access authentication state
* Less secure than httpOnly cookies

Production recommendation:

* httpOnly cookies
* CSRF protection
* Refresh token rotation
* Server-side session validation

The localStorage approach is accepted for MVP delivery speed.



## Day 8 - Authorization Enforcement Strategy

### ADR-014: Route-Level Role Enforcement

**Context**

Administrative operations require stricter access control than standard employee operations.

Examples:

* User management
* Department management
* Permission management
* Document administration

Authorization must be enforced consistently across all administrative endpoints.

### Decision

Protect all administrative routes using:

```python
require_admin()
```

Administrative access rule:

```python
current_user.role == "admin"
```

Authorization behavior:

```text
No Token
    ↓
401 Unauthorized

Valid User Token
    ↓
403 Forbidden

Valid Admin Token
    ↓
Access Granted
```

The legacy Day 3 authentication header was completely removed.

### Consequences

Benefits:

* Centralized role enforcement
* Consistent security model
* Simple authorization logic
* Easy extension for future roles

Tradeoffs:

* Role hierarchy currently limited to simple comparisons

Future enhancement:

* Fine-grained permission engine
* Resource-level authorization
* Department-aware access control

These enhancements are scheduled for Day 9 and subsequent retrieval phases.



## Day 9 - Permission Policy Architecture

### ADR-015: Policy-Based Authorization Framework

**Context**

The platform must support multiple authorization strategies over time.

Current requirements are department-based:

* HR users access HR documents
* Engineering users access Engineering documents
* Public content is accessible across departments
* Administrators require unrestricted access

Future enterprise deployments may require:

* Attribute-Based Access Control (ABAC)
* Role-Based Access Control (RBAC)
* Row-Level Security (RLS)
* Tenant-specific authorization models

Embedding authorization rules directly into retrieval logic would tightly couple security enforcement to implementation details and make future expansion difficult.

### Decision

Introduce a PermissionPolicy abstraction.

```python
class PermissionPolicy(ABC):

    async def get_allowed_departments(...)

    async def get_allowed_visibilities(...)

    async def can_access_document(...)
```

The initial implementation uses:

```python
DepartmentPermissionPolicy
```

which evaluates access using:

* User role
* User department
* Permission rules stored in PostgreSQL
* Document visibility metadata

All runtime authorization decisions flow through the policy abstraction.

### Consequences

Benefits:

* Separation of authorization from retrieval
* Easy introduction of alternative policy models
* Improved testability
* Enterprise-friendly architecture

Tradeoffs:

* Additional abstraction layer
* Slight increase in implementation complexity

Future enhancement:

* ABAC policies
* Tenant-aware policies
* External authorization providers



## Day 9 - Permission Enforcement Strategy

### ADR-016: Two-Layer Authorization Enforcement

**Context**

Unauthorized content must never reach the language model.

Vector databases perform metadata filtering during retrieval, but relying solely on vector-store filtering creates a single point of failure.

Potential risks include:

* Incorrect metadata
* Query construction bugs
* Retrieval implementation changes
* Future vector database migrations

A defense-in-depth strategy is required.

### Decision

Enforce permissions at two independent layers.

Layer 1:

```text
Vector Database Filtering
```

Authorization filters are generated before retrieval:

```python
{
    "$and": [
        {
            "department_id": {
                "$in": allowed_departments
            }
        },
        {
            "visibility": {
                "$in": allowed_visibilities
            }
        }
    ]
}
```

The filter is passed directly into:

```python
VectorStore.query(where=...)
```

Layer 2:

```text
Application-Level Validation
```

Every retrieved chunk is re-evaluated using:

```python
PermissionPolicy.can_access_document()
```

Any chunk failing the secondary validation is discarded and logged as a security event.

### Consequences

Benefits:

* Defense-in-depth security
* Protection against retrieval edge cases
* Consistent authorization enforcement
* Safer future retrieval evolution

Tradeoffs:

* Small additional processing cost
* Duplicate validation logic

This tradeoff is accepted because authorization correctness is more important than retrieval performance.



## Day 9 - Runtime Policy Registry

### ADR-017: Pluggable Permission Registry

**Context**

Authorization strategies may change across deployments.

Examples:

* Department-based access
* Attribute-based access
* Customer-specific access models
* Regulatory compliance policies

Hard-coding policy implementations would require application changes whenever authorization requirements evolve.

### Decision

Introduce a runtime policy registry.

```python
register_permission_policy(
    name,
    policy_class
)
```

```python
get_policy(
    sql_store,
    name="department"
)
```

Default policy:

```python
DepartmentPermissionPolicy
```

The registry allows policy selection without changing retrieval or authorization services.

Example future registrations:

```python
register_permission_policy(
    "abac",
    ABACPolicy
)

register_permission_policy(
    "row_level",
    RLSPolicy
)
```

### Consequences

Benefits:

* Extensible authorization architecture
* Reduced coupling
* Easier experimentation
* Future enterprise flexibility

Tradeoffs:

* Additional indirection layer
* More objects participating in authorization flow

The flexibility gained outweighs the additional complexity.



## Day 10 - Hybrid Retrieval Strategy

### ADR-018: Hybrid Retrieval Architecture

### Context

Semantic vector retrieval provides strong conceptual matching but may miss exact keyword matches.

Keyword retrieval using BM25 performs well for exact terms but lacks semantic understanding.

A retrieval strategy is required that balances both approaches.

### Decision

Implement a hybrid retrieval pipeline combining:

```text
Vector Search
+
BM25 Search
```

Results from both retrievers are merged using weighted scoring:

```text
final_score =
(VECTOR_WEIGHT * vector_score)
+
(KEYWORD_WEIGHT * bm25_score)
```

Current weights:

```text
VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3
```

### Consequences

#### Benefits

- Better retrieval accuracy
- Improved exact-match handling
- Strong semantic understanding

#### Tradeoffs

- Additional retrieval computation
- More complex scoring logic

---

## Day 10 - Runtime Retriever Registry

### ADR-019: Pluggable Retrieval Framework

### Context

The system currently supports:

- `VectorRetriever`
- `BM25Retriever`
- `HybridRetriever`

Future retrieval approaches may include graph retrieval, metadata retrieval, or external search providers.

Hard-coding retrieval implementations would increase coupling.

### Decision

Introduce a retriever registry:

```python
register_retriever(...)
get_retriever(...)
```

Default retriever:

```python
HybridRetriever
```

Retrieval implementations can be replaced without changing downstream application logic.

### Consequences

#### Benefits

- Extensible retrieval architecture
- Easier experimentation
- Reduced coupling

#### Tradeoffs

- Additional abstraction layer


## Day 11 - Retrieval Pipeline Orchestration

### ADR-020: Centralized Retrieval Pipeline

### Status

Accepted

### Context

Hybrid retrieval produces candidate chunks using vector search and BM25 retrieval.

As the retrieval process expands to include permission validation, reranking, audit logging, and future LLM integration, coordinating these stages directly inside API endpoints would increase coupling and duplicate logic.

A centralized orchestration layer is required to execute the complete retrieval workflow.

### Decision

Introduce a dedicated `RetrievalPipeline` service responsible for the complete retrieval process.

```text
User Query
      │
      ▼
Hybrid Retrieval
      │
      ▼
Permission Filter
      │
      ▼
Reranker (Day 12)
      │
      ▼
Final Top-K
      │
      ▼
Audit Logging
```

The retrieval pipeline performs:

- Candidate retrieval
- Secondary permission validation
- Reranking (placeholder for Day 12)
- Final Top-K selection
- Audit logging

All future chat endpoints and AI agents access organizational knowledge exclusively through this pipeline.

### Consequences

#### Benefits

- Single entry point for knowledge retrieval
- Clear separation between orchestration and retrieval algorithms
- Simplifies future reranker integration
- Consistent retrieval workflow across the platform

#### Tradeoffs

- Additional orchestration layer
- Slight increase in service complexity

---

## Day 11 - Defense-in-Depth Retrieval Security

### ADR-021: Secondary Permission Validation

### Status

Accepted

### Context

Candidate retrieval already applies department-aware filtering through:

- Chroma metadata filtering
- PostgreSQL department filtering

Although storage-level filtering prevents unauthorized retrieval under normal operation, relying solely on infrastructure-level filtering increases the impact of implementation mistakes or future retrieval changes.

A second authorization layer is required before retrieved chunks are returned to the application.

### Decision

Introduce a secondary permission validation stage within the `RetrievalPipeline`.

```text
Hybrid Retrieval
        │
Storage-Level Filtering
        │
PermissionService.filter_chunks()
        │
Authorized Chunks
```

Every candidate chunk is validated against the current user's permissions before it becomes eligible for reranking or response generation.

Every retrieval request is additionally recorded in the audit log to provide a complete compliance trail.

### Consequences

#### Benefits

- Defense-in-depth security model
- Prevents accidental data exposure
- Independent validation of storage-layer filtering
- Complete audit trail for all retrieval operations

#### Tradeoffs

- Small additional processing overhead
- Most retrieval requests will not remove additional chunks because storage filtering already enforces permissions


## Day 12 - Cross-Encoder Reranking

### ADR-022: Cross-Encoder Reranking Pipeline

### Status
Accepted

### Context

Hybrid retrieval produces relevant candidate chunks using vector search and BM25 scoring.

Although effective, hybrid scores cannot jointly evaluate the relationship between the complete user query and the complete document chunk.

A secondary ranking stage is required to improve the relevance of the final context returned to the LLM.

### Decision

Introduce a reranking stage after permission filtering.

```text
Hybrid Retrieval
        │
Permission Filter
        │
Cross-Encoder Reranker
        │
Final Top-K
```

The default reranker uses:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker:

- Receives authorized candidate chunks
- Computes query-document relevance scores
- Updates the ranking score
- Returns candidates sorted by descending relevance

### Consequences

#### Benefits

- Improved retrieval precision
- Better final context selection
- Higher quality input for LLM generation

#### Tradeoffs

- Additional inference latency
- Extra memory usage for the CrossEncoder model

---

## Day 12 - Pluggable Reranker Framework

### ADR-023: Runtime Reranker Registry

### Status
Accepted

### Context

The system currently supports:

- `CrossEncoderReranker`
- `ScoreReranker`

Future deployments may use different reranking models depending on performance, hardware, or deployment requirements.

Hard-coding reranker selection would increase coupling between the retrieval pipeline and reranker implementations.

### Decision

Introduce a runtime reranker registry:

```python
register_reranker(...)
get_reranker(...)
```

The active reranker is selected using the configuration:

```text
RERANKER_TYPE
```

Supported implementations:

- `cross_encoder`
- `score`

The retrieval pipeline depends only on the reranker interface, allowing implementations to be replaced without modifying pipeline logic.

### Consequences

#### Benefits

- Extensible reranking architecture
- Configurable deployment options
- Reduced coupling between retrieval and reranking

#### Tradeoffs

- Additional abstraction layer
- Registry maintenance for new reranker implementations


## Day 13 - Generator & Grounded Response

### ADR-024: Generation Service Architecture

### Status

Accepted

### Context

Hybrid retrieval and cross-encoder reranking produce a small set of authorized document chunks. A dedicated generation layer is required to transform these chunks into grounded natural language responses while preventing hallucinations and maintaining source traceability.

Generation should remain independent of the underlying LLM provider to allow future migration between providers without affecting the rest of the retrieval pipeline.

### Decision

Introduce a dedicated generation layer consisting of:

- LLM provider abstraction
- Citation builder
- Generator service
- Chat service orchestration
- Session management
- Metrics recording

The generation flow is:

User Query
→ Retrieval Pipeline
→ Citation Builder
→ Generator
→ LLM Provider
→ Grounded Response

All generation requests interact only with the `LLMProvider` interface. Provider-specific implementations (currently Groq) remain isolated behind the abstraction layer.

The generator never invokes the LLM when no authorized context is available, preventing unsupported responses.

### Consequences

Positive

- Provider-independent architecture
- Reduced hallucination risk
- Fully grounded responses
- Persistent conversation history
- Built-in observability
- Future support for streaming and multiple providers

Negative

- Additional orchestration layer
- Slight increase in implementation complexity

## Frozen Prompt v1

The following system prompt is frozen for Version 1 of the generation pipeline.

```text
You are a knowledge assistant for an organization.

Answer the user's question using ONLY the provided document context.

Do not use any external knowledge.

If the context does not contain enough information to fully answer the question, clearly state that the available information is insufficient.

Reference supporting sources using [1], [2], etc.

Be concise, factual, and avoid speculation.
```


---

## Day 14 - Retrieval Relevance Quality Gate

### ADR-025: Rerank-Based Quality Gate

### Status

Accepted

### Context

During Week 2 security validation, several queries without relevant supporting documents still returned grounded responses.

Although authorization correctly prevented access to restricted content, unrelated authorized chunks could still be passed to the language model because retrieval always returned the highest-scoring available chunks.

Examples:

- "What is finance policy?" for an Engineering employee
- "What are salary adjustment guidelines?" when no relevant document existed

These responses were factually grounded in retrieved documents but were semantically unrelated to the user's question.

### Decision

Introduce a retrieval quality gate after reranking and before generation.

```text
Hybrid Retrieval
        │
        ▼
Permission Filter
        │
        ▼
Cross-Encoder Reranker
        │
        ▼
Quality Gate
        │
        ▼
Final Top-K
        │
        ▼
Generation
```

The gate evaluates the highest reranker score.

If the top reranker score is below the configured threshold, no chunks are forwarded to the language model.

Instead, the generator returns the standard authorization fallback response.

**Current configuration:**

```text
MIN_RERANK_SCORE = 0.0
```

### Consequences

#### Benefits

- Reduces false-positive retrieval
- Prevents irrelevant grounded responses
- Improves response precision
- Maintains existing security guarantees

#### Tradeoffs

- Some borderline queries may now return the fallback response instead of a low-confidence answer.

---

## Day 14 - Week 2 Security Validation

### ADR-026: Defense-in-Depth Retrieval Security Validation

### Status

Accepted

### Context

Week 2 introduced authentication, permission-aware retrieval, cross-department access control, reranking, and grounded generation.

Before beginning the agent architecture, the complete security model required validation.

### Decision

A comprehensive security validation suite was executed covering:

- Department isolation
- Public document access
- Cross-department permission rules
- Restricted document visibility
- JWT signature validation
- Retrieval audit logging

The validation confirmed that:

- Unauthorized chunks never reach the language model.
- Restricted documents are excluded during retrieval using metadata filtering.
- Application-level permission validation remains in place as a secondary authorization layer.
- Invalid JWT signatures are rejected before authorization.
- Every retrieval request produces a complete audit trail.

### Consequences

#### Benefits

- Verified defense-in-depth security architecture
- Confirmed permission correctness before introducing AI agents
- Improved auditability
- Increased confidence in retrieval correctness


## Day 15 - Agent orchestration
### ADR-027: Agent-Based Orchestration Architecture

**Status**

Accepted

## Context

The Week 2 implementation executes the Retrieval-Augmented Generation (RAG) pipeline directly through `ChatService`.

```text
ChatService
    │
    ▼
RetrievalPipeline
    │
    ▼
Generator
```

While effective for a single retrieval workflow, this architecture provides no structured mechanism for introducing intermediate reasoning, planning, or future AI capabilities.

Upcoming features require multiple independent processing stages, including:

- Query planning
- Multi-query retrieval
- Response generation
- Session memory
- Future reviewer and tool agents

Embedding all of these responsibilities into `ChatService` would increase coupling and make future extensions difficult.

## Decision

Introduce an agent orchestration layer using **LangGraph**.

The workflow is modeled as a directed graph where each agent performs exactly one responsibility while operating on a shared workflow state.

```text
ChatService
      │
      ▼
LangGraph Workflow
      │
      ▼
Planner
      │
      ▼
Research
      │
      ▼
Response
```

Each node receives an `AgentState`, updates only the fields it owns, and returns the modified state.

The workflow is compiled once during application startup and reused throughout the application's lifetime.

## Consequences

### Positive

- Separates orchestration from business logic.
- Agents remain independently testable.
- New agents can be introduced without modifying existing workflow components.
- Supports future branching workflows and conditional execution.
- Keeps `ChatService` focused on request orchestration rather than reasoning.

### Negative

- Introduces an additional abstraction layer.
- Slightly increases project complexity during early development.

---

## Dat 15 - Agent state
### ADR-028: Shared Agent State Contract

**Status**

Accepted

## Context

Multiple agents participate in the workflow and must exchange information between execution stages.

Passing arbitrary dictionaries between agents creates several risks:

- Inconsistent field names
- Runtime key errors
- Difficult debugging
- Poor maintainability as additional agents are introduced

The workflow therefore requires a single, well-defined state contract.

## Decision

Introduce a shared `AgentState` using `TypedDict`.

The state represents the complete lifecycle of a chat request and contains:

- User query
- Serialized user context
- Retrieval strategy
- Planned search queries
- Retrieved chunks
- Generated answer
- Citations
- Confidence score
- Execution trace

Each agent owns only a subset of these fields.

| Agent | Fields Modified |
|--------|-----------------|
| Planner | `retrieval_strategy`, `search_queries`, `trace` |
| Research | `retrieved_chunks`,`no_results`, `trace` |
| Response | `answer`, `citations`, `confidence`, `trace` |

The workflow state remains serializable to ensure compatibility with LangGraph execution.

## Consequences

### Positive

- Strongly typed workflow contract.
- Clear ownership of state fields.
- Simplifies debugging and testing.
- Enables future visualization of workflow execution.
- Compatible with future persistence and checkpointing.

### Negative

- State structure must evolve carefully as new workflow features are added.


## Day 16 - Research Agent

### ADR-029: Multi-Query Research Agent

### Status

**Accepted**

---

## Context

The Planner Agent determines the optimal retrieval strategy and may generate multiple search queries for a single user request.

Executing only the original user query would ignore the planner's reasoning and reduce retrieval coverage.

The workflow therefore requires a dedicated **Research Agent** responsible for executing all planned queries while preserving the platform's existing permission-aware retrieval pipeline.

To maintain security and consistency, the Research Agent must not bypass established retrieval components or perform independent database or vector store operations.

---

## Decision

Introduce a dedicated **Research Agent** responsible for executing the retrieval stage of the agent workflow.

For each planned search query, the Research Agent:

- Executes the existing `RetrievalPipeline`
- Aggregates retrieved chunks
- Deduplicates chunks using `chunk_id`
- Preserves the highest `rerank_score` for duplicate chunks
- Sorts the final chunk set by reranking score
- Limits results to `settings.FINAL_TOP_K`
- Stores the resulting context in `AgentState`

The Research Agent performs no language generation and accesses no storage systems directly.

### Workflow

```text
Planner
    │
    ▼
Search Queries
    │
    ▼
Research Agent
    │
    ▼
RetrievalPipeline
    │
    ▼
Authorized Chunks
```

The agent also records execution metadata within the shared workflow trace and sets a `no_results` flag when no authorized retrieval context is available.

---

## Consequences

### Positive

- Separates retrieval from planning and response generation.
- Reuses the existing permission-aware retrieval pipeline.
- Supports multi-query retrieval without duplicating results.
- Preserves defense-in-depth security through centralized permission enforcement.
- Provides deterministic workflow state for downstream agents.
- Enables future retrieval strategies without modifying the Response Agent.

### Negative

- Executes multiple retrieval operations for complex queries, increasing retrieval latency.
- Adds additional aggregation and deduplication logic within the workflow.


## Day 17 - Full agent pipeline

## ADR-030: Multi-Agent Response Generation

## Status

Accepted

## Context

The original chat pipeline directly invoked the retrieval pipeline followed by the response generator.

As the system evolves toward a multi-agent architecture, response generation should become an explicit workflow stage executed after planning and research.

## Decision

Introduce a dedicated Response Agent responsible for:

- handling retrieval failures
- invoking the Generator
- updating the shared AgentState
- producing citations
- computing confidence
- recording execution traces

The Generator remains responsible for all LLM interaction, preserving a single source of truth for prompt construction and response generation.

## Consequences

Advantages

- clear separation of responsibilities
- reusable Generator
- simpler workflow orchestration
- easier future expansion with additional agents

Trade-offs

- one additional orchestration layer
- AgentState carries final response metadata


## Day 17 - Citation engine

## ADR-031: Structured Citation Engine

## Status

Accepted

## Context

Generated answers must reference their original knowledge sources in a structured and consistent manner.

Documents may originate from paginated sources (PDF) or non-paginated sources such as DOCX and TXT.

## Decision

Enhance the Citation Builder to:

- merge citations belonging to the same document
- preserve page references for PDFs
- generate section references for non-paginated documents
- include representative excerpts
- retain chunk indexes for future debugging and UI features

## Consequences

Benefits

- improved explainability
- reduced duplicate citations
- support for heterogeneous document formats



## Day 18 - Confidence Layer

### ADR-032: Confidence Classification Layer

**Status**

Accepted

## Context

Earlier versions of the generation pipeline returned a single numeric confidence value computed from the average retrieval similarity score.

Although useful, a numeric score alone is difficult for both users and downstream interfaces to interpret.

The system requires a confidence model that is both machine-readable and human-friendly while remaining grounded in retrieval quality.

## Decision

Replace the previous confidence calculation with a confidence classification layer.

The Generator now returns:

- `confidence_score` (0–100)
- `confidence_level`
  - `high`
  - `medium`
  - `low`

Classification is based on:

- highest retrieval score
- number of supporting retrieved chunks

The confidence layer remains retrieval-based rather than LLM-based, ensuring that confidence reflects evidence quality instead of model certainty.

## Consequences

### Benefits

- easier interpretation for end users
- supports confidence badges in the UI
- confidence remains deterministic
- better downstream analytics and evaluation

### Trade-offs

- confidence becomes rule-based instead of a continuous similarity metric
- confidence thresholds require occasional tuning as retrieval evolves

---

## Day 18 - Session Memory

### ADR-033: Session Conversation Memory

**Status**

Accepted

## Context

The original chat pipeline treated every request as an isolated interaction.

This prevented follow-up questions from using previous conversation context, forcing users to restate topics in every request.

A lightweight conversation memory mechanism is required while keeping retrieval and generation responsibilities separate.

## Decision

Introduce a dedicated `SessionMemory` service responsible for:

- retrieving recent conversation history
- formatting history using the standard OpenAI message format
- enforcing the maximum session retention policy
- supporting conversation-aware generation

Session lifecycle management remains the responsibility of `SessionService`.

Conversation history is injected into the workflow before response generation and supplied to the Generator alongside the current user request.

## Consequences

### Benefits

- enables multi-turn conversations
- preserves clean separation between session lifecycle and memory management
- reusable for future memory strategies
- minimal impact on retrieval performance

### Trade-offs

- one additional database query per request
- longer prompts for follow-up conversations

---

## Day 18 - Conversational Query Resolution

### ADR-034: Query Resolution Layer

**Status**

Accepted

## Context

Session memory enables the language model to understand conversational context during response generation.

However, retrieval quality remains poor for ambiguous follow-up questions because the Planner receives only the latest user message.

Questions such as:

> "How many days is that?"  
> "Explain it."  
> "What about HR?"

lack sufficient context for effective retrieval.

## Decision

Introduce a dedicated `QueryResolver` component executed before planning.

The `QueryResolver`:

- detects conversational follow-up questions using lightweight heuristics
- rewrites ambiguous questions into standalone natural-language queries using recent conversation history
- leaves standalone questions unchanged
- validates rewritten queries before allowing them into the retrieval pipeline
- falls back to the original query whenever rewriting fails

The Planner and Research stages operate on the resolved query, while the Generator continues answering the user's original question.

## Consequences

### Benefits

- significantly improves retrieval quality for follow-up questions
- preserves modular agent responsibilities
- avoids increasing Planner prompt complexity
- minimizes additional LLM calls through conservative heuristics
- provides a scalable foundation for future conversational retrieval enhancements

### Trade-offs

- introduces an additional preprocessing stage
- ambiguous follow-up questions incur one extra LLM request
- rewrite quality depends on conversation history and prompt quality

---

## Day 18 - Agent Workflow Enhancement

### ADR-035: Conversation-Aware Agent Pipeline

**Status**

Accepted

## Context

The original LangGraph workflow executed planning, research, and response generation using only the current user query.

To support conversational interactions, the workflow must incorporate session history and resolved queries without changing the responsibilities of existing agents.

## Decision

Extend the shared `AgentState` with:

- conversation history
- resolved retrieval query
- confidence score
- confidence level

The workflow now performs the following sequence:

1. Session history retrieval
2. Conversational query resolution
3. Planning
4. Research
5. Response generation

The Generator receives:

- original user query
- retrieved context
- conversation history

while retrieval operates exclusively on the resolved query.

## Consequences

### Benefits

- conversation awareness across the entire pipeline
- improved retrieval accuracy
- preserved separation of concerns
- minimal changes to existing agents

### Trade-offs

- slightly richer shared workflow state
- additional orchestration before planning



# Day 19 - Complete Audit Logging & Observability

## ADR-036: Enterprise Audit Logging Architecture

### Status

**Accepted**

### Context

As the Smart Knowledge Bank platform evolves into an enterprise knowledge system, security and compliance require a complete audit trail of significant system events.

Prior implementations recorded only selected events (such as login and retrieval queries), leaving administrative operations without consistent audit coverage.

Additionally, administrators require an API for reviewing historical audit events for compliance, security investigations, and enterprise demonstrations.

### Decision

Introduce a centralized audit logging strategy across all business services.

The following events are now recorded:

- User login
- User logout
- Document uploaded
- Document ingested
- Chat query execution
- Permission denied
- User creation
- Permission rule changes

Audit logs are written directly from the service responsible for the business action, ensuring that logging remains coupled with the business event rather than HTTP endpoints.

An administrative API has been introduced:

```http
GET /api/v1/admin/audit-logs
```

The endpoint supports:

- User filtering
- Action filtering
- Date range filtering
- Pagination
- Joined user email information
- Reverse chronological ordering

Dedicated schemas and an `AuditService` encapsulate audit retrieval logic, keeping routers free of SQL.

### Consequences

#### Positive

- Complete compliance audit trail.
- Consistent enterprise logging.
- Administrative audit dashboard support.
- Clear separation between API routing and business logic.
- Future audit enhancements can be implemented without changing routers.

#### Negative

- Audit logging remains implemented individually across services.
- Future refactoring may introduce a shared `AuditLogger` abstraction to eliminate duplicated audit write logic.

---

## ADR-037: Safe Observability & Agent Metrics

### Status

**Accepted**

### Context

The platform originally recorded only endpoint-level metrics during chat execution.

As the architecture evolved into a multi-agent workflow, endpoint metrics alone were insufficient for understanding execution performance.

Additionally, failures while recording observability data should never interrupt business operations.

### Decision

Introduce a dedicated `ObservabilityCollector` that wraps the lower-level `MetricsRecorder`.

Responsibilities include:

- Safe metric recording
- Exception isolation
- Endpoint metrics
- Agent metrics
- Success/failure tracking

All observability writes are executed through the collector, preventing metrics failures from affecting application requests.

Metrics are now recorded for:

- `/api/v1/chat/query`
- `/api/v1/auth/login`
- `/api/v1/admin/documents`

Each agent additionally records individual execution metrics:

- Planner Agent
- Research Agent
- Response Agent

Planner token usage is now preserved, and endpoint metrics aggregate total request token consumption by summing planner and response generation tokens.

Agent-specific helper methods were introduced to remove duplicated metric recording logic while maintaining a single observability interface.

### Consequences

#### Positive

- Metrics recording can no longer crash application requests.
- Per-agent latency becomes visible.
- Total request token accounting is more accurate.
- Reduced code duplication through shared helper methods.
- Provides the foundation for future tracing and observability dashboards.

#### Negative

- Metrics are now recorded at both endpoint and agent levels, increasing the number of stored metric records.
- Research Agent currently reports zero token usage because it performs retrieval without LLM interaction.