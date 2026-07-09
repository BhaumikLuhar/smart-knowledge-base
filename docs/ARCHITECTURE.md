# Smart Knowledge Bank Architecture

## Overview

Smart Knowledge Bank is a Retrieval-Augmented Knowledge Management platform that allows organizations to upload, process, store, and retrieve internal knowledge documents.

Week 1 establishes the ingestion and retrieval foundation:

* Document upload
* Department organization
* Metadata management
* Document chunking
* Embedding generation
* Vector storage
* Semantic search
* Administrative knowledge base management

---

# High-Level Architecture

```text
┌─────────────────────┐
│      Next.js        │
│      Frontend       │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│      FastAPI        │
│      API Layer      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Knowledge Layer   │
│ Business Services   │
└──────────┬──────────┘
           │
           ├───────────────┐
           │               │
           ▼               ▼
┌─────────────────┐  ┌─────────────────┐
│   SQL Store     │  │  Vector Store   │
│  PostgreSQL     │  │     Chroma      │
└─────────────────┘  └─────────────────┘
```

The application follows a layered architecture where business services never communicate directly with PostgreSQL or Chroma.

All database access is routed through SQLStore.

All vector database access is routed through VectorStore.

---

# Backend Structure

```text
backend/
│
├──core/
|   ├── auth/
|   ├── cache/
|   ├── conversation/
|   ├── generation/
|   ├── knowledge/
|   ├── memory/
|   ├── observability/
|   ├── permissions/
|   ├── profiling/
|   ├── retrieval/
|   ├── config.py
|   └── database.py
│
├── routers/
│   ├── admin.py
│   ├── auth.py
│   ├── chat.py
│   └── documents.py
│
├── storage/
│   ├── files/
│   ├── sql/
│   ├── vector/
│   └── vector_db/
│
└── scripts/
```

---

# Frontend Structure

```text
frontend/
│
├── app/
│   ├── dashboard/
│   ├── knowledge-base/
│   ├── chat/
│   ├── users/
│   └── settings/
│
├── components/
│   ├── knowledge/
│   ├── ui/
│   └── sidebar.tsx
│
├── services/
├── types/
└── lib/
```

---

# Knowledge Layer

The Knowledge Layer contains all business logic.

Current services:

### KnowledgeService

Responsibilities:

* Validate uploads
* Register documents
* Create document records
* Start ingestion workflow

---

### DepartmentService

Responsibilities:

* Department management
* Department document queries
* Metadata updates
* Soft delete operations

---

### PermissionService

Responsibilities:

* Create permission rules
* Validate department access mappings

---

### FileService

Responsibilities:

* File validation
* Extension validation
* File size validation
* Disk storage
* Filename sanitization

---

# Storage Layer

## SQLStore

Central PostgreSQL abstraction.

Responsibilities:

* Save records
* Query records
* Update records
* Delete records
* Bulk chunk insertion
* Execute raw reporting queries

Application services do not import asyncpg directly.

---

## VectorStore

Central Chroma abstraction.

Responsibilities:

* Save embeddings
* Query embeddings
* Delete vectors
* Count vectors

Application services do not import chromadb directly.

---

# Document Ingestion Pipeline

The ingestion pipeline runs asynchronously through FastAPI BackgroundTasks.

Flow:

1. Admin uploads document
2. FileService saves file to disk
3. Document row created in PostgreSQL
4. Background ingestion task starts
5. Document status changes to processing
6. Appropriate loader parses document text
7. Chunker generates overlapping chunks
8. Chunks inserted into PostgreSQL
9. Embedder generates vector embeddings
10. VectorStore saves embeddings into Chroma
11. Chunk embedding references updated
12. Audit log entry created
13. Document status changes to ready

Failure path:

```text
processing
    ↓
exception
    ↓
failed
```

Failure details are stored in:

```text
documents.metadata.ingestion_error
```

---

# Loader Architecture

Loaders are registered through a central registry.

Current loaders:

* PDF Loader
* DOCX Loader
* TXT Loader
* Markdown Loader

Selection occurs automatically through file extension matching.

---

# Chunking Strategy

Current chunking configuration:

```text
Chunk Size: 800 characters
Overlap: 100 characters
```

Process:

1. Split document into sentences
2. Build chunks until size threshold reached
3. Preserve overlap between chunks
4. Store metadata with each chunk

Stored metadata:

```text
document_id
department_id
visibility
chunk_index
page_number
```

---

# Embedding Architecture

Embedding Model:

```text
BAAI/bge-small-en-v1.5
```

Vector Dimension:

```text
384
```

Implementation:

Singleton pattern.

Benefits:

* Model loaded once
* Reduced memory usage
* Faster inference

Query embeddings use BGE query prefixing:

```text
Represent this sentence for searching relevant passages:
```

---

# Retrieval Architecture

Current retrieval process:

1. User query received
2. Hybrid retrieval (Vector + BM25)
3. Metadata filtering
   - department
   - visibility
4. Secondary permission validation
5. Cross-Encoder reranking
6. Retrieval quality gate
7. Final Top-K
8. Audit logging
9. Context returned to the Generator

Current metadata filters:

```python
{
    "department_id": "<department-id>"
}
```

Current metadata filtering enforces both:

- Department permissions
- Document visibility

before retrieval.

Application-level permission validation provides a second authorization layer before reranking.

---

# Performance Optimization Layer

Week 4 introduces several performance optimizations while preserving the existing retrieval and generation behavior.

The optimization strategy focuses on reducing latency without changing retrieval quality, authorization, or response generation.

---

## Multi-Level Cache Architecture

```text
                 User Query
                      │
                      ▼
          Pipeline Response Cache
             │             │
      Cache Hit        Cache Miss
             │             │
             ▼             ▼
        Return Response   Agent Workflow
                              │
                              ▼
                     Parallel Research
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       Vector Retrieval                 BM25 Retrieval
                                              │
                                              ▼
                                        BM25 Cache
```

Implemented cache layers:

- Pipeline response cache
- BM25 index cache
- Cached public department lookup
- Cached permission metadata

> **Note:** Cache invalidation occurs whenever indexed knowledge changes.

---

## Parallel Execution

Several independent stages execute concurrently.

### Research Stage

Planner-generated search queries execute retrieval simultaneously before results are merged and deduplicated.

```text
            Planner
               │
               ▼
      ┌────────┬────────┬────────┐
      ▼        ▼        ▼
   Query 1   Query 2   Query 3
      │        │        │
      └────────┴────────┴────────┘
                 │
                 ▼
        Merge + Deduplicate
```

### Persistence Stage

Independent database writes execute concurrently.

```text
        Assistant Response
                │
                ▼
 ┌──────────────┬──────────────┬──────────────┬──────────────┐
 ▼              ▼              ▼              ▼
User Msg   Assistant Msg    Metrics      Audit Log
```

This reduces response latency while preserving existing persistence behavior.

---

## Performance Profiling

A lightweight profiler measures execution time throughout the request lifecycle.

Measured stages include:

- Session lookup
- Planner execution
- Hybrid retrieval
- Query embedding
- Chroma search
- Permission filtering
- CrossEncoder reranking
- Retrieval audit logging
- Generator execution
- Parallel persistence
- Complete workflow

The profiler reports:

- Total execution time
- Average execution time
- Minimum execution time
- Maximum execution time
- Invocation count

> **Note:** Profiling is diagnostic only and does not affect application behavior.

---

# Database Schema

## departments

```text
id
name
display_name
description
created_at
```

---

## users

```text
id
email
hashed_password
full_name
role
department_id
created_at
```

---

## documents

```text
id
name
original_filename
file_path
file_type
department_id
visibility
version
status
page_count
uploaded_by
metadata
created_at
updated_at
```

---

## chunks

```text
id
document_id
text
chunk_index
page_number
embedding_ref
department_id
visibility
created_at
```

---

## permissions

```text
id
role
department_id
can_access_department_id
```

---

## sessions

```text
id
user_id
token
expires_at
```

---

## audit_logs

```text
id
user_id
action
resource_type
resource_id
details
ip_address
created_at
```

---

## metrics

```text
id
metric_name
metric_value
created_at
```

---

# Extension Points

## Loader Registry

New document types can be added without modifying ingestion logic.

Example:

```python
register_loader(".xlsx", ExcelLoader())
```

---

## Vector Store Interface

The application communicates only with VectorStore.

Future vector databases can replace Chroma without changing business services.

Potential replacements:

* Pinecone
* Weaviate
* Qdrant
* pgvector

---

# Security Boundaries

Current architecture enforces:

```text
Knowledge Layer
    ↓
Storage Layer
    ↓
Database
```

Forbidden:

```text
core/knowledge → asyncpg
core/knowledge → chromadb

core/retrieval → asyncpg
core/retrieval → chromadb
```

## Retrieval Security Model

Authorization is enforced using two independent layers.

Layer 1

Storage-level filtering:

- Chroma metadata filters
- PostgreSQL visibility filters

Only accessible chunks are eligible for retrieval.

Layer 2

Application-level validation:

PermissionService validates every retrieved chunk before reranking.

This defense-in-depth architecture ensures unauthorized content never reaches the language model even if retrieval implementations change.

All persistence operations must pass through storage abstractions.

---

# Current Platform Capabilities

Implemented

* JWT authentication
* Role-based authorization
* Department-aware permissions
* Hybrid retrieval
* Cross-Encoder reranking
* Retrieval quality gates
* Grounded response generation
* Citation generation
* Multi-agent LangGraph workflow
* Conversation-aware retrieval
* Session persistence
* Enterprise audit logging
* Observability and metrics
* Administrative dashboard
* User management
* Knowledge base management
* Complete chat interface
* Frontend role protection
* Settings page
* Shared loading spinner component
* Reusable frontend error cards
* Consistent empty-state components
* Session-based chat interface
* Agent execution reasoning display
* Confidence visualization
* Multi-level in-memory caching
* Parallel research execution
* Parallel persistence pipeline
* Request-level performance profiling
* Permission metadata caching
* BM25 index caching


## Retrieval Pipeline

The Retrieval Pipeline provides a centralized orchestration layer for knowledge retrieval.

```text
User Query
      │
      ▼
Pipeline Cache
      │
      ▼
Planner
      │
      ▼
Parallel Research Retrieval
      │
      ▼
Hybrid Retriever
      │
      ▼
Metadata Filtering
      │
      ▼
Permission Validation
      │
      ▼
Cross-Encoder Reranker
      │
      ▼
Retrieval Quality Gate
      │
      ▼
Generator
      │
      ▼
Parallel Persistence
```


---

## Generation Layer

Week 2 introduces the generation layer responsible for producing grounded, permission-aware responses from authorized retrieval results.

```text
Client
│
▼
Chat Router
│
▼
ChatService
│
├──────────────────────────┐
▼                          ▼
SessionService        RetrievalPipeline
                           │
                           ▼
                    Hybrid Retrieval
                           │
                           ▼
                 Metadata Filtering
          (Department + Visibility)
                           │
                           ▼
              Secondary Permission Filter
                           │
                           ▼
                Cross-Encoder Reranker
                           │
                           ▼
                Retrieval Quality Gate
                           │
                           ▼
                      Generator
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
  Citation Builder                  LLM Provider
                                            │
                                            ▼
                                     Groq Provider
```

### Responsibilities

#### ChatService

Coordinates the complete RAG request lifecycle.

Responsibilities:

* Session management
* Message persistence
* Retrieval execution
* Response generation
* Metrics recording

---

#### RetrievalPipeline

Executes the complete retrieval workflow.

Responsibilities:

* Hybrid retrieval
* Metadata filtering
* Secondary permission validation
* Cross-encoder reranking
* Retrieval quality validation
* Audit logging

The pipeline guarantees that only authorized and sufficiently relevant context reaches the Generator.

---

#### SessionService

Manages conversation sessions and validates ownership.

---

#### Generator

Transforms authorized retrieval context into grounded natural language responses.

Responsibilities:

* Build prompts
* Invoke the configured LLM provider
* Compute response confidence
* Generate citations
* Return structured responses
* Return a fallback response when no authorized or relevant context exists

The Generator never invokes the LLM when retrieval returns no usable context.

---

#### Citation Builder

Aggregates citations by document, removes duplicate references, and preserves page and chunk metadata.

---

#### LLM Provider

Defines the provider abstraction.

Current implementation:

* Groq (OpenAI-compatible API)

Future providers can be added without changing the generation pipeline.



## Agent Workflow

## Agent Pipeline (Week 3)

The complete chat workflow combines conversational memory, LangGraph orchestration, retrieval, and grounded response generation.

```text
Client
   │
   ▼
Chat UI
   │
   ▼
Chat Router
   │
   ▼
ChatService
   │
   ▼
SessionService
(load history)
   │
   ▼
Conversation Resolver
(resolve retrieval query)
   │
   ▼
run_agent_pipeline()
   │
   ▼
Planner Agent
   │
   ▼
Research Agent
   │
   ▼
Response Agent
   │
   ▼
Generator
   │
   ▼
Groq Provider
```

Shared AgentState contains:

- original query
- resolved query
- conversation history
- retrieval strategy
- search queries
- retrieved chunks
- citations
- confidence score
- confidence level
- reasoning trace

### Agent responsibilities

#### Planner Agent

- analyzes the request
- determines retrieval strategy
- generates optimized search queries

#### Research Agent

- executes permission-aware retrieval
- aggregates and deduplicates retrieved chunks
- preserves retrieval trace

#### Response Agent

- generates grounded responses
- builds citations
- computes confidence
- records execution trace




---

# Frontend Architecture

The frontend is implemented using Next.js with feature-oriented pages and reusable UI components.

```text
Frontend
│
├── Dashboard
├── Knowledge Base
├── Chat
├── Users
└── Settings
```

Application state is divided into:

- Authentication (AuthContext)
- API Services
- Feature Components

## Chat UI architecture

```text
Chat Page
│
├── Chat Sidebar
│     ├── Session History
│     └── New Chat
│
├── Chat Window
│     ├── User Messages
│     ├── Assistant Messages
│     │      ├── Confidence Badge
│     │      ├── Citation Panel
│     │      └── Reasoning Panel
│     │
│     ├── Typing Indicator
│     ├── Loading Spinner
│     └── Error Card
│
└── Chat Input
```

Administrative pages are protected through both frontend role checks and backend authorization.

API communication is centralized through service modules that encapsulate all HTTP requests.

This separation keeps presentation components independent from backend implementation details while allowing future UI changes without affecting business logic.



## Shared UI Infrastructure

To provide a consistent user experience across all pages, the frontend reuses common presentation components.

Shared UI behaviors include:

- Loading spinner component
- Error card component
- Empty-state messaging
- Feature-oriented service layer
- Centralized API helper
- Authentication context
- Reusable UI primitives

Pages remain focused on business logic while presentation concerns are shared through reusable components.

---

# Registry Extension System

The Smart Knowledge Bank uses registry-based extension points to keep major subsystems open for extension while avoiding modifications to existing business logic.

Each registry follows the same principle:

- Register a new implementation
- Retrieve the implementation through the registry
- Business logic never depends on concrete classes

This allows new capabilities to be added without modifying existing workflows.

---

## Loader Registry

Location

```
core/knowledge/loaders/factory.py
```

Current implementation

- PDFLoader
- DocxLoader
- TxtLoader
- MarkdownLoader

How to add a new loader

1. Create a class inheriting `DocumentLoader`.
2. Implement `load()` and `supported_extension()`.
3. Register it:

```python
register_loader(".xlsx", ExcelLoader)
```

Do NOT change

- KnowledgeService
- IngestionService
- get_loader()

The loader registry automatically resolves implementations by file extension.

---

## Retriever Registry

Location

```
core/retrieval/registry.py
```

Current implementation

- HybridRetriever (default)

Supports runtime injection for testing.

How to add a new retriever

1. Implement the `Retriever` interface.
2. Register it:

```python
register_retriever(
    "graph",
    GraphRetriever,
)
```

3. Inject it when required:

```python
inject_retriever("graph")
```

Do NOT modify

- RetrievalPipeline
- ResearchAgent

These always retrieve implementations through the registry.

---

## Permission Policy Registry

Location

```
core/permissions/registry.py
```

Current implementation

- DepartmentPermissionPolicy

How to add a new permission model

1. Implement `PermissionPolicy`.
2. Register:

```python
register_permission_policy(
    "attribute_based",
    ABACPolicy,
)
```

3. Activate through controlled code configuration.

Do NOT expose policy selection through any public API.

Permission enforcement must remain entirely server-controlled.

---

## Tool Registry

Location

```
tools/registry.py
```

Current implementation

Generic Tool interface.

Future tools may include

- Calculator Tool
- Web Search Tool
- SQL Tool
- Knowledge Graph Tool

Register example

```python
register_tool(
    "calculator",
    CalculatorTool,
)
```

Do NOT modify agent implementations when adding tools.

Agents should request tools through the registry only.

---

## Agent Registry

Location

```
agents/registry.py
```

Current implementation

- PlannerAgent
- ResearchAgent
- ResponseAgent

How to add a new workflow agent

1. Create a class inheriting `Agent`.
2. Register:

```python
register_agent(
    "reviewer",
    ReviewerAgent,
)
```

3. Add the required workflow edge in `workflow.py`.

No existing agents require modification.

This keeps the LangGraph workflow extensible while preserving existing agent implementations.